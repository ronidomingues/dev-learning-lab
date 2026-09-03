# 27 · Alternativas e quando não usar Power BI

**Nível:** intermediário
**Data:** 14/08/2026

Todo material sobre uma ferramenta tende ao entusiasmo. Este capítulo é o contrapeso:
onde o Power BI é a escolha errada, o que compete com ele, e como decidir com honestidade.

---

## 1. Quando o Power BI é a escolha errada

### 1.1 Quando o problema não é de BI

| Você quer | Ferramenta certa |
|---|---|
| Registrar transações | ERP, sistema transacional |
| Guardar o dado mestre | Banco de dados, MDM |
| Emitir faturas e boletos | Relatório paginado, sistema fiscal |
| Modelagem estatística séria | R, Python, ferramenta estatística |
| Monitorar processo em tempo real (segundos) | SCADA, historiador, Real-Time Intelligence |
| Aplicação com escrita intensiva | Aplicação web |
| Documento que alguém vai imprimir e assinar | Word, LaTeX, relatório paginado |

**O sintoma de estar usando errado:** você está lutando contra a ferramenta. Se toda tarefa
exige um truque, provavelmente é a ferramenta errada.

### 1.2 Quando o ambiente não comporta

- **Nenhuma máquina Windows disponível para desenvolvimento.** É contornável
  ([`03`](03-instalacao.md) §4–5), mas é atrito permanente.
- **Restrição legal de que o dado não saia da empresa** e sem orçamento para Report Server.
- **Empresa não usa Microsoft 365** — o principal argumento comercial (já está no
  contrato) desaparece, e você paga cheio.
- **Público final majoritariamente externo** — Embedded custa e complica.

### 1.3 Quando três gráficos resolvem

Se a necessidade é "mostrar três números que mudam uma vez por mês para cinco pessoas",
uma planilha ou uma página HTML resolve. Power BI traz licença, governança, atualização e
manutenção — todo esse aparato tem custo, e ele só se paga com escala ou recorrência.

---

## 2. Comparação com os concorrentes

Avaliação honesta, com data. **É opinião fundamentada, não medição.**

### 2.1 Tableau

| Critério | Quem ganha |
|---|---|
| Exploração visual livre | **Tableau**, com folga |
| Estética padrão | **Tableau** |
| Modelagem e camada semântica | **Power BI** |
| Linguagem de cálculo | **Power BI** (DAX é mais poderoso que os cálculos do Tableau) |
| Preço | **Power BI**, com folga |
| Mac nativo | **Tableau** |
| Governança corporativa | Empate técnico |
| Comunidade em português | **Power BI** |

**Quando escolher Tableau:** cultura de análise exploratória, times de Mac, orçamento
confortável, e quando a qualidade visual é parte do produto entregue ao cliente.

### 2.2 Looker (Google)

O diferencial é o **LookML**: a camada semântica é **código**, versionado em Git, com
revisão e testes — desde 2012. Isso influenciou toda a indústria e é, conceitualmente,
superior ao que o Power BI só alcançou em 2024 com PBIP/TMDL.

**Quando escolher Looker:** empresa no Google Cloud, cultura de engenharia forte, prioridade
absoluta em "métrica como código".

**Custo:** caro, e a experiência de exploração para o usuário final é inferior à do Power BI
e à do Tableau.

### 2.3 Qlik Sense

O **modelo associativo** é genuinamente diferente: em vez de filtros que propagam por
relações, ele mostra o que está associado e — o que é único — **o que não está**
(valores excluídos aparecem em cinza).

Para análise investigativa, é uma vantagem real que nem Power BI nem Tableau têm.

**Por que perdeu mercado:** preço, e um modelo de licenciamento historicamente complicado.

### 2.4 Metabase, Apache Superset, Redash

Open source. O apelo é claro: sem licença por usuário, autogerenciado, SQL direto.

| Ganha | Perde |
|---|---|
| Custo de licença zero | Custo de operação (alguém hospeda e mantém) |
| SQL direto, sem camada intermediária | Sem camada semântica robusta |
| Rápido de subir | Sem modelo em memória — desempenho depende do banco |
| Sem aprisionamento | Recursos corporativos limitados (RLS, governança) |

**Quando escolher:** startups e times de engenharia com bom banco analítico, onde o público
é técnico e a governança é leve. **Metabase** é notavelmente bom para essa faixa.

**Cuidado com a conta:** "grátis" ignora o custo de hospedar, atualizar, monitorar e
sustentar. Para 50 usuários, meia pessoa dedicada custa mais que 50 licenças Pro.

### 2.5 Excel

O concorrente real, e o que mais gente subestima.

**Excel ganha quando:** o dado é pequeno, o usuário é um só, a análise é ad hoc, ou a
resposta é "eu preciso mexer nos números com as mãos". Nenhuma ferramenta de BI substitui
isso, e tentar é perder tempo.

**Estratégia madura:** não brigue com o Excel — **conecte-o ao modelo**. "Analisar no
Excel" ([`23`](23-servico-colaboracao-e-atualizacao.md) §5.1) dá ao usuário a interface
que ele quer com os números que a empresa aprova.

### 2.6 Ferramentas de código (Python + Streamlit/Dash/Observable)

**Ganham:** flexibilidade total, controle de versão nativo, integração com ML, sem licença.

**Perdem:** custo de desenvolvimento por relatório, ausência de autosserviço (o usuário
não constrói nada sozinho), e você reimplementa filtros, drill, exportação e segurança.

**Quando escolher:** produtos analíticos com visualização muito específica, ou saída de
modelos de ML que precisa de interatividade sob medida.

### 2.7 Panorama comparativo

| | Power BI | Tableau | Looker | Qlik | Metabase | Excel |
|---|---|---|---|---|---|---|
| Preço | ★★★★★ | ★★ | ★ | ★★ | ★★★★★ | ★★★★ |
| Autosserviço | ★★★★ | ★★★★★ | ★★ | ★★★★ | ★★★ | ★★★★★ |
| Modelagem | ★★★★★ | ★★★ | ★★★★ | ★★★★ | ★★ | ★ |
| Camada semântica | ★★★★ | ★★★ | ★★★★★ | ★★★ | ★★ | ✘ |
| Exploração visual | ★★★ | ★★★★★ | ★★★ | ★★★★ | ★★★ | ★★ |
| Governança | ★★★★ | ★★★★ | ★★★★ | ★★★ | ★★ | ✘ |
| Versionamento | ★★★★ | ★★ | ★★★★★ | ★★ | ★★★ | ✘ |
| Multiplataforma (autoria) | ★★ | ★★★★★ | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ |
| Comunidade PT-BR | ★★★★★ | ★★★ | ★ | ★★ | ★★ | ★★★★★ |

*Avaliação do autor em 14/08/2026. Escala relativa entre estas ferramentas, não absoluta.*

---

## 3. Como decidir de verdade

Perguntas na ordem em que importam:

**1. Quem vai construir?** Analistas de negócio → Power BI ou Tableau. Engenheiros →
Metabase, Superset, código. Ambos → Power BI com camada semântica.

**2. Quem vai consumir, e quantos?** 5 pessoas → licença por usuário. 5.000 → capacidade
ou open source. Externos → Embedded ou algo pensado para isso.

**3. Onde estão os dados?** Ecossistema Microsoft → Power BI. Google Cloud → considere
Looker. Databricks/Snowflake → qualquer um funciona bem.

**4. Que orçamento, e qual modelo de custo?** Custo por usuário cresce com adoção; custo de
capacidade é fixo; open source troca licença por trabalho.

**5. Que maturidade de dados existe?** Sem data warehouse, toda ferramenta vai sofrer. **A
ferramenta de BI não conserta arquitetura de dados** — e essa é a decisão que mais gente
erra: comprar BI para resolver um problema de engenharia de dados.

**6. Que competência existe no time e no mercado local?** No Brasil, o mercado de Power BI
é ordens de grandeza maior que o de qualquer alternativa. Isso importa para contratar e
para ser contratado.

---

## 4. Coexistência

Não é raro — nem errado — ter mais de uma.

**Padrões que funcionam:**

- **Power BI corporativo + Metabase para engenharia.** O time de dados consulta SQL direto
  no Metabase; o negócio consome modelos governados no Power BI.
- **Power BI + Excel conectado.** Já discutido; é o padrão maduro.
- **Power BI + notebooks.** Análise exploratória e ML em Python; resultados publicados
  como tabela consumida pelo Power BI.
- **Power BI + relatórios paginados.** Interativo para análise, paginado para documento.

**Padrão que não funciona:** duas ferramentas de BI para o **mesmo** público com os
**mesmos** números. Isso garante divergência e a pergunta "qual está certo?", que é a
morte da confiança.

---

## 5. Os riscos de escolher Power BI

Honestidade sobre o que você assume ao escolher.

| Risco | Mitigação |
|---|---|
| **Aprisionamento em DAX e M** | Não têm equivalente fora do ecossistema. Mantenha a lógica de negócio na **fonte** (SQL/dbt) sempre que possível |
| **Aumentos de preço** | Aconteceu em 2025 (+40% no Pro). Revise licenciamento anualmente |
| **Windows para autoria** | Planeje VMs ou Windows 365 se seu time não é Windows |
| **Cadência mensal** | Recursos em preview mudam; algo pode quebrar. Padronize a versão do time |
| **Pressão para o Fabric** | Avalie com números, não com narrativa ([`26`](26-fabric-e-ecossistema.md) §6) |
| **Proliferação de modelos** | Governança desde o começo ([`24`](24-seguranca-e-governanca.md)) |

**A mitigação mais valiosa, e vale repetir:** **mantenha a lógica de negócio o mais à
esquerda possível** — na fonte, em SQL versionado. Um modelo Power BI fino sobre um data
warehouse bem modelado é substituível em semanas. Um modelo com 300 medidas contendo
regras que não existem em lugar nenhum é um casamento sem divórcio.

---

## 6. Os cinco porquês: por que o Power BI domina o mercado se não é o melhor em tudo?

1. **Por que o líder não é o tecnicamente superior?**
   Porque a decisão de compra corporativa não pondera qualidade técnica acima de tudo.
   Ela pondera custo total, risco, disponibilidade de mão de obra e esforço de aquisição.

2. **Por que o Power BI ganha nesses critérios?**
   Preço um quinto do concorrente; já incluído no contrato Microsoft 365 (aquisição quase
   sem atrito); ferramenta de autoria gratuita (adoção antes da compra); e o maior
   mercado de profissionais.

3. **Por que a distribuição vence a qualidade?**
   Porque o custo de **adotar** uma ferramenta nova (processo de compra, segurança,
   treinamento, migração) frequentemente supera a diferença de qualidade entre duas
   ferramentas boas. Se a ferramenta B é 20% melhor e custa 5× mais, além de exigir um
   projeto de aquisição, a conta raramente fecha.

4. **Por que isso não é injusto com o Tableau?**
   Porque não é uma competição de mérito técnico isolado — é uma competição de **valor
   entregue por unidade de custo total**. O Tableau continua sendo melhor em exploração
   visual e continua vendendo para quem valoriza isso o bastante.

5. **Parada legítima — economia de plataforma e custo de troca.**
   É um resultado conhecido em mercados de plataforma: incumbentes com distribuição
   ampla e custos de troca altos vencem entrantes melhores, salvo salto de ordem de
   grandeza. Mesma dinâmica do Office nos anos 1990, do Windows, do Android.
   **A lição prática:** ao avaliar tecnologia, separe "qual é melhor" de "qual vou usar".
   São perguntas diferentes, com respostas legitimamente diferentes.

---

## 7. Autoteste

1. Cite quatro problemas para os quais o Power BI é a ferramenta errada.
2. Qual é o sintoma de estar usando a ferramenta errada?
3. Em que o Tableau é melhor, e quando escolhê-lo?
4. O que é o LookML e por que ele foi influente?
5. O que o modelo associativo do Qlik faz que os outros não fazem?
6. Qual o custo escondido do BI open source?
7. Qual é a estratégia madura em relação ao Excel?
8. Quais são as seis perguntas de decisão, na ordem?
9. Que padrão de coexistência **não** funciona, e por quê?
10. Qual é a mitigação mais valiosa contra o aprisionamento, e por quê?
11. Explique por que a distribuição vence a qualidade em mercados de plataforma.

---

**Próximo:** [`60-teoria-avancada.md`](60-teoria-avancada.md) — os limites teóricos.
