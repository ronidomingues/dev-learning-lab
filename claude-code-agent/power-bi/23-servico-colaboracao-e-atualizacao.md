# 23 · Serviço, colaboração e atualização

**Nível:** intermediário
**Data:** 14/08/2026

Um `.pbix` na sua máquina não é um produto. Este capítulo trata do que acontece depois de
publicar: onde o conteúdo vive, quem o vê, como se atualiza e como não virar bagunça.

---

## 1. Workspaces

> **Workspace** — a unidade de organização e colaboração no Power BI Service. Contém
> modelos semânticos, relatórios, dataflows, apps e (no Fabric) lakehouses, notebooks e
> pipelines.

### 1.1 Tipos

| Tipo | Uso |
|---|---|
| **Meu workspace** | Pessoal. Ninguém mais vê. Rascunho |
| **Workspace de equipe** | Colaboração real. É onde tudo de verdade acontece |

**Regra:** nada que outra pessoa dependa deve viver no "Meu workspace". Quando essa pessoa
sai da empresa, o conteúdo vai junto. É a causa nº 1 de relatório órfão.

### 1.2 Funções

| Função | Ver | Editar | Publicar app | Gerenciar acesso | RLS aplicada? |
|---|---|---|---|---|---|
| **Visualizador** | ✔ | ✘ | ✘ | ✘ | **Sim** |
| **Colaborador** | ✔ | ✔ | ✘ | ✘ | **Não** |
| **Membro** | ✔ | ✔ | ✔ | parcial | **Não** |
| **Administrador** | ✔ | ✔ | ✔ | ✔ | **Não** |

> **A coluna mais importante é a última.** A RLS só se aplica a **Visualizadores**.
> Colocar um usuário restrito como "Membro" anula toda a segurança que você escreveu.
> Ver [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md).

### 1.3 Organização de workspaces

O padrão que funciona em empresas de porte médio:

```
WS-Vendas-DEV          ← desenvolvimento (poucos, com acesso de edição)
WS-Vendas-TESTE        ← homologação (donos de negócio validam)
WS-Vendas-PROD         ← produção (só o pipeline publica aqui)
   └── App "Vendas"    ← o que os 300 usuários realmente acessam
```

Ligados por um **pipeline de implantação** ([`25`](25-ciclo-de-vida-e-devops.md)).

**Antipadrão comum:** um workspace por relatório. Vira dezenas de workspaces, permissões
inconsistentes e ninguém acha nada. Organize por **domínio de negócio**, não por artefato.

---

## 2. A camada semântica corporativa

Este é o padrão que mais gera valor duradouro e o menos praticado.

### 2.1 O problema que ele resolve

Sem camada semântica:

```
Analista A: pbix próprio → sua definição de "faturamento"
Analista B: pbix próprio → outra definição
Analista C: pbix próprio → terceira definição
Diretoria: três números diferentes na mesma reunião
```

Com camada semântica:

```
     ┌─────────────────────────────────────────┐
     │  MODELO SEMÂNTICO CORPORATIVO           │
     │  mantido pelo time de dados             │
     │  · definições oficiais                  │
     │  · RLS                                  │
     │  · certificado / promovido              │
     └──────┬──────┬──────┬──────┬─────────────┘
            │      │      │      │
      relatório  relat.  Excel  Copilot/agente
       oficial   do ana-  (Ana-
                 lista   lisar)
```

### 2.2 Como se implementa

1. **Publique o modelo separadamente** dos relatórios. Um `.pbix` só com dados, modelo e
   medidas; nenhuma página de relatório.
2. **Habilite "Permitir que usuários criem conteúdo com base neste modelo"**
   (permissão *Build*).
3. **Relatórios conectam por conexão dinâmica**: no Desktop, Obter dados → Modelos
   semânticos do Power BI.
4. **Endosse o modelo:** *Promovido* (o dono atesta) ou *Certificado* (a governança
   atesta). Aparece com selo na busca.
5. **Publique um app** para os consumidores finais.

### 2.3 O que os analistas ganham e o que perdem

**Ganham:** dados prontos, medidas oficiais, atualização automática, RLS já resolvida,
zero manutenção de ETL.

**Perdem:** não podem alterar o modelo. Se precisarem de uma coluna nova, precisam pedir.

**A ponte é o modelo composto** ([`20`](20-modos-de-armazenamento.md) §6.2): o analista
conecta ao modelo corporativo **e acrescenta** suas tabelas locais. Governança e agilidade
ao mesmo tempo — com o custo de que mudanças no modelo central podem quebrar o derivado.

---

## 3. Distribuição

### 3.1 As cinco formas, e o que cada uma implica

| Forma | Público | Licença | Quando |
|---|---|---|---|
| **Acesso ao workspace** | Time que constrói | Pro (ou F64+) | Colaboração |
| **Compartilhar item** | Poucas pessoas | Pro para todos | Casos pontuais |
| **App organizacional** ★ | Muitos consumidores | Pro para todos, ou F64+ | **O padrão para distribuição** |
| **Incorporar (Teams/SharePoint)** | Quem tem acesso ao item | Igual ao item | Onde as pessoas já estão |
| **Publicar na Web** ☠ | **Internet inteira, sem login** | Nenhuma | **Nunca**, salvo dado público |

### 3.2 Aplicativos organizacionais (*org apps*)

Passaram a GA em **julho/2026**, com **audiências** — e isso mudou o padrão de
distribuição.

Uma **audiência** é um subconjunto de conteúdo entregue a um grupo:

```
App "Vendas"
├── Audiência "Diretoria"     → páginas de resumo e margem
├── Audiência "Gerentes"      → resumo + detalhe da equipe (com RLS)
└── Audiência "Vendedores"    → só o painel individual
```

Um único app, três experiências. Antes disso, era preciso publicar três apps ou aceitar
que todo mundo via tudo.

**Novidades de julho/2026 nos org apps**, segundo a documentação:

- audiências em **GA**;
- **indicadores** (bookmarks) do autor e pessoais funcionam dentro do app;
- **Storytelling no PowerPoint** a partir de conteúdo do app;
- **APIs REST de CRUD** para apps e audiências — ou seja, dá para automatizar a
  distribuição;
- audiências também no **aplicativo móvel**.

**Por que usar app em vez de dar acesso ao workspace:**

1. O consumidor não vê rascunhos nem itens intermediários.
2. Você controla **quando** a versão vai ao ar (publicar o app é um ato deliberado).
3. Navegação organizada e personalizada.
4. Permissões mais simples de auditar.

### 3.3 "Publicar na Web" — o alerta

Torna o relatório **público na internet, sem autenticação, indexável por buscadores**.

É a maior fonte documentada de vazamento de dados com Power BI. Já apareceram em
buscadores: folhas de pagamento, dados de pacientes, listas de clientes com CNPJ.

**Ação para administradores:** desligue no locatário (Configurações de administração →
Publicar na Web → Desabilitado, ou permitido apenas para um grupo específico com
aprovação). **Faça isso hoje.**

**Uso legítimo:** dados genuinamente públicos — indicadores de transparência, painel
municipal aberto, dados de campanha. Nesses casos, é uma ferramenta excelente.

---

## 4. Atualização de dados

### 4.1 Configuração

Modelo semântico → **Configurações**:

| Seção | O que fazer |
|---|---|
| **Credenciais da fonte** | Autenticar cada fonte. Sem isso, nada atualiza |
| **Conexão do gateway** | Se houver fonte on-premises |
| **Atualizar** | Fuso horário, horários, e-mail de falha |
| **Parâmetros** | Alterar sem republicar ★ |

**Limites:** 8 atualizações/dia no Pro; 48 em PPU/capacidade; via **API ou XMLA**, sem
limite prático de contagem (mas sujeito ao consumo da capacidade).

### 4.2 Atualização incremental

Ver [`06-exemplos.md`](06-exemplos.md) §14 para o passo a passo completo.

Resumo do que importa:

1. Parâmetros `RangeStart` e `RangeEnd` (nomes exatos, tipo Data/Hora).
2. Filtro `>= RangeStart and < RangeEnd` — **nunca `<=`**, ou a fronteira duplica.
3. O filtro **precisa dobrar** (*folding*), senão o mecanismo é inútil.
4. Política: arquivar N anos, atualizar os últimos M dias.
5. A primeira atualização no Service é longa; em Pro pode estourar o limite de 2 h.

### 4.3 Quando a atualização falha

| Erro | Causa | Correção |
|---|---|---|
| `Credentials are missing` | Fonte sem credencial configurada | Configurações → Credenciais |
| `The gateway is offline` | Serviço parado ou portas bloqueadas | [`03`](03-instalacao.md) §7 |
| `Timeout` | Consulta lenta demais | Folding, incremental, ou capacidade |
| `Data source error: column not found` | A origem mudou | Corrija a consulta; considere `MissingField.Ignore` |
| `Resource governing: query exceeded memory` | Modelo maior que o SKU permite | Reduza ([`21`](21-vertipaq-por-dentro.md)) ou aumente o SKU |
| `Dynamic data source` | URL concatenada | [`06`](06-exemplos.md) §13 |

**Monitore.** Configure notificação por e-mail de falha e, em ambiente sério, um alerta que
chegue a alguém que age. Uma falha silenciosa por três dias produz decisões com dados
velhos — pior que nenhum relatório, porque ninguém desconfia.

---

## 5. Consumo

### 5.1 Analisar no Excel

Modelo semântico → ⋯ → **Analisar no Excel**. Baixa um `.odc` que abre uma tabela dinâmica
**ao vivo** conectada ao modelo.

**Por que isto importa mais do que parece:** boa parte dos usuários de negócio quer Excel.
Em vez de brigar contra isso, dê a eles Excel **conectado ao modelo governado**, com as
medidas oficiais e a RLS aplicada. É a diferença entre um Excel que reflete a verdade
oficial e um Excel copiado e colado que diverge no dia seguinte.

### 5.2 Teams e SharePoint

Incorporação nativa. Em julho/2026 a incorporação no SharePoint ganhou uma UI para
selecionar o workspace diretamente (em vez de colar URL) e um alternador para
**incorporar um visual único**.

### 5.3 Assinaturas e alertas

- **Assinatura:** e-mail agendado com PDF ou imagem da página. Bom para quem não abre
  relatório.
- **Alerta de dados:** notificação quando um valor cruza um limite (definido sobre blocos
  de painel ou visuais suportados).
- **Data Activator / Real-Time Intelligence:** para regras mais sofisticadas, no Fabric.

### 5.4 Exportação

| Formato | Limite típico |
|---|---|
| PDF / PowerPoint | Layout fixo |
| Excel (resumido/subjacente) | 150.000 linhas |
| CSV | 30.000 linhas |
| Analisar no Excel | Sem limite (é consulta ao vivo) |
| API `ExportTo` | Automatizável |

*Limites mudam; confirme antes de prometer.*

---

## 6. Ciclo de vida do conteúdo

O que ninguém planeja e todo mundo sofre.

| Fase | Ação |
|---|---|
| **Nascimento** | Dono definido, propósito escrito, fonte documentada |
| **Vida** | Monitorar uso; corrigir; comunicar mudanças |
| **Envelhecimento** | Uso caindo? Fonte mudou? Regra mudou? |
| **Morte** | **Aposentar formalmente.** Avisar, arquivar, remover |

**A métrica de uso** existe: workspace → item → **Métricas de uso**. Um relatório com
zero acessos em 90 dias é candidato à aposentadoria — e cada relatório aposentado é uma
fonte a menos de número divergente.

**Opinião do autor:** o maior problema de governança de BI não é a falta de relatórios; é o
excesso. Empresas com 400 relatórios ativos e 40 realmente usados são a norma. Aposentar
é trabalho de gente sênior, e ninguém ganha crédito por isso.

---

## 7. Os cinco porquês: por que separar modelo de relatório?

1. **Por que publicar o modelo separado dos relatórios?**
   Porque um modelo pode servir a muitos relatórios, e um relatório serve a um público.
   São ciclos de vida diferentes.

2. **Por que os ciclos são diferentes?**
   O modelo muda quando a **regra de negócio** ou a fonte muda — raro e controlado. O
   relatório muda quando a **pergunta** muda — frequente e descentralizado.

3. **Por que isso importa na prática?**
   Porque, juntos, cada alteração de layout exige republicar o modelo inteiro, o que
   significa recarregar todos os dados e arriscar a atualização. Separados, publicar um
   relatório é instantâneo e sem risco.

4. **Por que não basta ter cuidado ao publicar?**
   Porque "cuidado" não escala. Com 5 analistas publicando, alguém vai sobrescrever o
   modelo com uma versão de desenvolvimento. Separar **torna o erro impossível**, em vez
   de desaconselhado — o mesmo princípio de ocultar colunas técnicas
   ([`14`](14-modelagem-dimensional.md)).

5. **Parada legítima — princípio geral de engenharia.**
   Isto é uma instância de **separação de responsabilidades** (*separation of concerns*),
   articulada por Dijkstra em 1974: partes que mudam por razões diferentes e em ritmos
   diferentes devem poder mudar independentemente. É o mesmo princípio que separa esquema
   de aplicação, API de cliente, e conteúdo de apresentação. Não é convenção do Power BI;
   é convenção da engenharia de software, aplicada aqui.

---

## 8. Autoteste

1. Por que nada importante deve viver no "Meu workspace"?
2. Qual função de workspace **não** tem RLS aplicada, e qual a consequência?
3. Como se organiza workspaces em empresa média, e qual é o antipadrão?
4. O que é uma camada semântica corporativa e qual problema resolve?
5. O que os analistas ganham e perdem com ela, e qual é a ponte?
6. Cite as cinco formas de distribuição e a que nunca deveria estar habilitada.
7. O que é uma audiência de org app e qual problema ela resolveu em julho/2026?
8. Por que usar app em vez de dar acesso ao workspace? Dê quatro razões.
9. Na atualização incremental, por que `<` e não `<=`? E por que o folding é essencial?
10. Por que "Analisar no Excel" é estratégico e não uma concessão?
11. Explique a separação modelo/relatório com o princípio de separação de responsabilidades.

---

**Próximo:** [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md).

---

*Fontes consultadas em 14/08/2026: [Microsoft Learn — What's new (julho/2026)](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new) (org apps com audiências em GA, bookmarks e storytelling em apps, CRUD APIs, embed no SharePoint); [Microsoft Learn — Get started with org apps](https://learn.microsoft.com/en-us/power-bi/explore-reports/org-app-items).*
