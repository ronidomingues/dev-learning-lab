# 65 · Estado da arte

**Nível:** pesquisa
**Data desta fotografia:** **14/08/2026**
**Validade estimada:** 3 a 6 meses. O Power BI atualiza mensalmente; este arquivo envelhece
mais rápido que qualquer outro do curso. **Reavalie a cada trimestre.**

> **Como ler este arquivo.** Separei o que é **fato documentado** (com fonte oficial), do
> que é **relato de terceiros** (blogs, comunidade), do que é **minha leitura** do que
> significa. Em um assunto que muda toda semana, essa separação vale mais que a informação.

---

## 1. O que aconteceu em 2026, até agosto

### 1.1 Fatos documentados em fontes oficiais

| Quando | O quê | Estado |
|---|---|---|
| **Junho/2026** | **Funções definidas pelo usuário em DAX (UDF)** — com parâmetros opcionais, dicas de tipo, suporte na modelagem web e criação direta na Exibição de Modelo | **GA** |
| Junho/2026 | Copilot na modelagem web | preview |
| Junho/2026 | Fabric Apps para modelos semânticos | preview |
| Junho/2026 | Shape map | GA |
| Junho/2026 | Seletor de data em segmentações | — |
| **Julho/2026** | **Org apps com audiências** | **GA** |
| Julho/2026 | Bookmarks (do autor e pessoais) dentro de org apps | — |
| Julho/2026 | Storytelling no PowerPoint a partir de org apps | — |
| Julho/2026 | **APIs REST de CRUD** para org apps, audiências e relatórios paginados | — |
| Julho/2026 | **Visão TMDL na web** | — |
| Julho/2026 | Opções de modelo (*Model options*) no Service | — |
| Julho/2026 | Painel de configurações de modelo semântico como padrão | preview (a partir de agosto) |
| Julho/2026 | Formatação condicional em gráficos de linha e em visuais com legenda | **GA** |
| Julho/2026 | Modern Visual Defaults com "Personalizar tema atual" | preview |
| Julho/2026 | `LOOKUP` em cálculos visuais aceita `AssociatedColumnsBehavior` com `INFERRED` | — |
| Julho/2026 | Descrição de medida via comentários `///` acima de `MEASURE` | — |
| Julho/2026 | Audiências de org app no aplicativo móvel | — |
| 2026 | **Modelos compostos com Direct Lake + tabelas Import** | preview |
| 2026 | **Semantic model authoring skill** — agente que cria modelos Direct Lake sobre lakehouse | documentado |
| **Outubro/2026** (anunciado) | Desativação do seletor de arquivos antigo: Desktop de março/2026 ou anterior perde salvar/compartilhar em OneDrive e SharePoint | **prazo** |

### 1.2 Relatado por terceiros (comunidade, blogs, cobertura do Build 2026)

Trato como **provável, não confirmado por mim** em fonte primária:

- **Fabric IQ** teria atingido GA no Build 2026 (junho), posicionado como "camada de
  contexto compartilhado" sobre dados estruturados no OneLake, com os modelos semânticos
  do Power BI como camada confiável para agentes.
- **Ontologias no Fabric IQ** — extensão dos modelos semânticos com entidades de negócio,
  relacionamentos, regras, ações e sinais em tempo real; **GA prevista** para os meses
  seguintes.
- **Integração com Microsoft Agent 365 como ferramenta MCP** de primeira parte, e acesso a
  ferramentas do Fabric IQ pelo **GitHub Copilot CLI** — perguntas em linguagem natural
  sobre dados do Fabric, relatórios e modelos semânticos, a partir do terminal.
- **Power BI Agent Skills** — agentes que constroem relatórios.

**Confirme antes de basear decisão de arquitetura nisso.** A distância entre um anúncio de
Build e um recurso estável em produção costuma ser de 6 a 18 meses.

---

## 2. A tendência de fundo: o modelo semântico vira API

**Minha leitura**, e é a coisa mais importante deste arquivo.

Por 17 anos, o modelo semântico do Power BI teve **um** consumidor real: o relatório do
Power BI (mais o Excel, na margem). Em 2026, os consumidores são:

```
                  ┌─────────────────────────────┐
                  │     MODELO SEMÂNTICO        │
                  │  · definições oficiais      │
                  │  · RLS                      │
                  │  · UDFs DAX tipadas         │
                  │  · descrições ///           │
                  └──┬────┬────┬────┬────┬──────┘
                     │    │    │    │    │
   relatório ────────┘    │    │    │    └──── agentes / MCP
   Excel ─────────────────┘    │    └───────── Microsoft 365 Copilot
   apps próprios (REST/XMLA) ──┘                aplicações de terceiros
```

**Três consequências práticas, e elas mudam prioridades de aprendizado:**

1. **Metadados viraram interface.** Nome de coluna, descrição de medida, sinônimo e
   formato deixaram de ser cosmética e passaram a ser **contrato de API**. Um agente que
   consome o modelo depende exatamente disso para acertar. Isso é o que já valia para o
   Q&A, agora com consequências maiores.

2. **UDFs em DAX são o "elo que faltava".** Lógica de negócio **reutilizável, tipada e
   versionável** é o que torna confiável tudo o que consome o modelo. Antes das UDFs, a
   mesma regra era copiada em 30 medidas, e a divergência era questão de tempo.

3. **A camada semântica virou o ativo estratégico**, e o relatório virou um dos consumidores
   — talvez nem o principal, daqui a alguns anos. Quem investir em modelagem e definições
   colhe em toda a superfície; quem investir em beleza de dashboard colhe num canal só.

**Se você quer uma única aposta de onde investir seu tempo de estudo em 2026, é esta.**

---

## 3. DAX UDF — o que mudou de verdade

GA em junho/2026, com parâmetros opcionais, dicas de tipo, criação na Exibição de Modelo do
Desktop e suporte na modelagem web.

```dax
DEFINE
    FUNCTION VariacaoPct = (
        Atual: NUMERIC,
        Anterior: NUMERIC,
        SeNulo: NUMERIC = BLANK()      -- parâmetro opcional
    ) =>
        IF(
            NOT ISBLANK( Anterior ) && Anterior <> 0,
            DIVIDE( Atual - Anterior, Anterior ),
            SeNulo
        )
```

E então, nas medidas:

```dax
Δ % vs AA  = VariacaoPct( [Faturamento], [Faturamento AA] )
Δ % Margem = VariacaoPct( [Margem %], [Margem % AA] )
Δ % Qtd    = VariacaoPct( [Quantidade], [Quantidade AA] )
```

**Por que isso importa mais do que parece:**

| Antes | Depois |
|---|---|
| A regra de "variação com tratamento de blank" copiada em 30 medidas | Uma função, 30 chamadas |
| Corrigir a regra = 30 edições | 1 edição |
| Divergência silenciosa entre medidas | Impossível |
| Nenhuma tipagem | Tipos declarados, erro em tempo de escrita |

**É a evolução mais significativa da linguagem desde os grupos de cálculo.** Junto com
TMDL e Git, o DAX finalmente tem as três coisas que fazem uma linguagem de negócio
sustentável: **abstração, tipos e versionamento**.

**Ressalva honesta:** GA em junho/2026 significa recente. Verifique a disponibilidade no
seu ambiente de destino (Report Server, versões antigas do Desktop, ferramentas de
terceiros) antes de depender disso em produção.

---

## 4. Copilot e agentes — onde estamos de verdade

### 4.1 O que funciona (minha avaliação, 14/08/2026)

| Tarefa | Avaliação |
|---|---|
| Explicar DAX existente | ★★★★☆ — genuinamente útil |
| Gerar DAX de padrão conhecido (YTD, variação, ranking) | ★★★☆☆ — bom, revise |
| Gerar descrições e sinônimos | ★★★★☆ — ótimo ponto de partida |
| Resumir o que está na tela | ★★★☆☆ |
| Gerar página de relatório | ★★☆☆☆ — ponto de partida, não entrega |
| Criar modelo semântico sobre lakehouse | ★★☆☆☆ — estrutura sim, semântica de negócio não |
| DAX com contexto de avaliação sutil | ★☆☆☆☆ — **plausível e errado**, o pior modo de falha |
| Decisões de modelagem | ★☆☆☆☆ — não conhece o seu negócio |
| Descobrir problemas de qualidade de dados | ★☆☆☆☆ |

### 4.2 O padrão que emergiu

O uso produtivo que observo não é "peça e receba". É:

```
humano define o problema e a regra de negócio
   → IA gera o esqueleto (DAX, transformação, descrição)
      → humano revisa contra um oráculo independente
         → humano publica e assume a responsabilidade
```

O passo do **oráculo independente** é o que separa uso profissional de fé. É exatamente o
que o `validar.py` do [`07-projeto-modelo/`](07-projeto-modelo/README.md) faz: calcula os
números fora do Power BI para conferir os de dentro.

### 4.3 O risco estrutural

**Opinião do autor, e é a mais forte deste arquivo.**

DAX gerado por IA é **plausível**. Compila, roda, devolve um número. Em ~80% dos casos
está certo; nos outros 20%, está sutilmente errado — um `ALL` onde deveria ser
`ALLSELECTED`, uma transição de contexto não intencional, um total que não fecha.

Como o número é plausível, ninguém confere. E como o BI serve para decidir, decide-se
errado com confiança.

**Isto é pior que o cenário sem IA**, onde o analista que não sabia DAX simplesmente não
entregava a medida — e a ausência era visível.

**A mitigação é chata e é a única que funciona:**

1. **Teste com oráculo independente** para toda medida crítica ([`25`](25-ciclo-de-vida-e-devops.md) §5.4).
2. **Revisão humana obrigatória** de DAX gerado, por alguém que saiba
   [`16`](16-dax-contexto-de-avaliacao.md).
3. **Nunca certifique** um modelo com medida gerada e não revisada.

**Corolário para a sua carreira:** a IA aumentou o valor de **saber avaliar** DAX e
diminuiu o valor de saber **digitar** DAX. Estude o capítulo 16, não a lista de funções.

---

## 5. Debates abertos no campo

### 5.1 Camada semântica: no BI ou fora dele?

| Posição | Argumento |
|---|---|
| **No BI** (Power BI, Looker) | Perto de quem consome; performance integrada; RLS e formatação juntas |
| **Fora** (dbt Semantic Layer, Cube) | Independente da ferramenta; testável; portável; não aprisiona |

**Minha posição:** híbrida, com uma regra clara — **regras de negócio estáveis e
compartilhadas** (o que é faturamento líquido, o que é um cliente ativo) pertencem à
**fonte**, em SQL versionado. **Regras dependentes de contexto de visualização** (% do
total visível, ranking dinâmico, comparações relativas) só existem no DAX e devem ficar
lá.

Essa divisão também é a melhor proteção contra aprisionamento
([`27-alternativas.md`](27-alternativas.md) §5).

### 5.2 Dashboards vão morrer?

A tese: com linguagem natural, ninguém mais precisará de dashboards.

**Contra-argumentos que considero decisivos:**

1. Dashboard é **monitoramento** (os mesmos indicadores, sempre), não exploração.
   Perguntar todo dia "quanto vendemos" é pior que olhar.
2. Confiança exige **reprodutibilidade**: o mesmo número, no mesmo lugar, todo dia.
3. Um número gerado por LLM não tem auditoria; um dashboard tem linhagem.

**Minha previsão:** o dashboard sobrevive como **camada de monitoramento**, e a exploração
migra para conversação. É complementaridade, não substituição. **Marque esta previsão e
me cobre em 2029.**

### 5.3 Self-service versus governança

Debate de 17 anos, sem solução. O que mudou: a IA facilitou tanto a criação que o volume
de conteúdo não governado explodiu.

**O que observo funcionar:** o modelo de três camadas de
[`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md) §7.1 — certificado,
promovido, exploratório — com a camada exploratória **explicitamente permitida**.
Governança que proíbe explorar empurra a exploração para o Excel, onde não há visibilidade.

### 5.4 Fabric é obrigatório?

**Comercialmente:** a pressão é grande e crescente.
**Tecnicamente:** não, para a maioria. Ver [`26-fabric-e-ecossistema.md`](26-fabric-e-ecossistema.md) §6.

**Minha leitura:** a Microsoft está deliberadamente colocando recursos novos (Direct Lake,
agentes, Fabric IQ, ontologias) atrás da capacidade F-SKU. Isso não torna o Fabric
necessário hoje, mas cria uma **divergência crescente de capacidades** entre quem tem e
quem não tem. Em 3 a 5 anos, "Power BI Pro puro" pode ser uma configuração legada.

**Recomendação prática:** não migre por pressão. Mas mantenha os dados em **formatos
portáveis** (Parquet/Delta) e a lógica de negócio **na fonte**, para que a migração, se
vier, seja uma decisão e não uma reconstrução.

---

## 6. O que observar nos próximos 12 meses

| Sinal | O que significaria |
|---|---|
| **Ontologias no Fabric IQ** chegarem a GA | O modelo semântico deixaria de ser só analítico e passaria a descrever entidades e ações de negócio — mudança conceitual grande |
| Adoção real de **MCP** sobre modelos semânticos | Modelo do Power BI como ferramenta padrão de agentes, fora do ecossistema Microsoft |
| Autoria completa no navegador | Fim da dependência de Windows; mudaria [`03-instalacao.md`](03-instalacao.md) inteiro |
| Evolução de preço | Depois de 2025, outro reajuste mudaria a matriz de decisão |
| Padrão aberto de camada semântica | Reduziria o aprisionamento; hoje é o maior risco do campo |
| Verificação formal de DAX | Se surgir, muda a relação com DAX gerado por IA |
| Concorrência séria em BI open source | Metabase/Superset ganhando camada semântica robusta |

---

## 7. Conselho para quem está aprendendo agora

**O que envelhece devagar (invista aqui):**

- modelagem dimensional — estável desde 1996;
- contexto de avaliação — estável desde 2009;
- compressão e cardinalidade — física, não moda;
- SQL — estável desde 1974;
- pensar sobre o dado que **não** está lá;
- ceticismo com números.

**O que envelhece rápido (aprenda quando precisar):**

- a interface;
- a lista de recursos em preview;
- os nomes comerciais (Fabric, Fabric IQ, Copilot, Agent…);
- os visuais da moda;
- os preços.

**Proporção que recomendo: 80% no primeiro grupo, 20% no segundo.** A maioria faz o
inverso, corre atrás de cada novidade mensal, e continua sem saber por que o total não
fecha.

---

## 8. Autoteste

1. O que atingiu GA em junho/2026 e por que é a evolução mais significativa da linguagem?
2. Qual a tendência de fundo de 2026 quanto ao papel do modelo semântico?
3. Por que "metadados viraram interface"?
4. Escreva uma UDF de variação percentual com parâmetro opcional.
5. Qual é o pior modo de falha do DAX gerado por IA, e por que é pior que não ter IA?
6. Descreva o padrão de uso produtivo de IA e o papel do oráculo independente.
7. Onde devem morar as regras de negócio estáveis, e onde as dependentes de contexto?
8. Dashboards vão morrer? Dê dois contra-argumentos.
9. Qual a recomendação prática diante da pressão pelo Fabric?
10. Cite três coisas que envelhecem devagar e três que envelhecem rápido.

---

*Fontes consultadas em 14/08/2026 — **oficiais**: [Microsoft Learn — What's new, julho/2026](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new); [Microsoft Learn — Change log do Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-change-log); [Microsoft Learn — Semantic model authoring skill](https://learn.microsoft.com/en-us/power-bi/developer/agentic/semantic-model-authoring-skill-overview); [Microsoft Learn — Direct Lake](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview); [Fabric Community — DAX User-Defined Functions (Generally Available)](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/DAX-User-Defined-Functions-Generally-Available/ba-p/5185738); [Fabric Community — Power BI June 2026 Feature Summary](https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/Power-BI-June-2026-Feature-Summary/ba-p/5193264); [Fabric Community — Fabric IQ](https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Fabric-IQ-The-shared-context-layer-for-AI-agents-and-real-time/ba-p/5191678); [Azure Blog — Build 2026](https://azure.microsoft.com/en-us/blog/microsoft-build-2026-building-agentic-apps-with-microsoft-fabric-and-microsoft-databases/). **Terceiros** (tratados como não confirmados): cobertura do Build 2026 em blogs e comunidade.*
