# 02 · Pré-requisitos

**Nível:** iniciante
**Data:** 14/08/2026

Este arquivo responde a três perguntas: **o que preciso saber**, **o que preciso ter** e
**quanto tempo isso vai levar de verdade**. A última resposta é a que mais desagrada,
e é a mais importante.

---

## 1. Conhecimento

### 1.1 Indispensável

Sem isto você trava no primeiro dia.

| Pré-requisito | Por quê | Onde aprender |
|---|---|---|
| **Operar um computador com Windows** | O Desktop é Windows-only; você vai instalar, mexer em pastas, lidar com permissões | Qualquer curso básico de informática |
| **Noção de tabela: linha, coluna, cabeçalho** | Todo o Power BI é tabela. Se "coluna" e "campo" não fazem sentido, nada faz | Excel básico |
| **Aritmética de negócio: soma, média, percentual, variação %** | Você vai escrever isso o dia inteiro | Ensino médio |
| **Entender o que sua empresa vende e como** | Sem contexto de negócio você produz gráficos verdadeiros e inúteis | Conversar com quem opera |

Note o que **não** está na lista: programação, SQL, estatística, matemática avançada.
Nenhum deles é indispensável para começar. Todos ajudam muito.

### 1.2 Ajuda muito (em ordem de retorno sobre o esforço)

| Pré-requisito | O que destrava | Onde aprender |
|---|---|---|
| **SQL — `SELECT`, `WHERE`, `GROUP BY`, `JOIN`** | Conectar direto no banco, entender *query folding*, e sobretudo **pensar em conjuntos** em vez de células | [`../sql/00-MAPA.md`](../sql/00-MAPA.md) desta pasta — comece em `12-consulta-select.md` |
| **Excel intermediário: tabela dinâmica, `PROCV`/`ÍNDICE+CORRESP`** | Tabela dinâmica é literalmente o modelo mental de uma matriz do Power BI | Curso gratuito da própria Microsoft |
| **Modelagem dimensional (fato × dimensão)** | O maior salto de qualidade que existe. É o assunto de [`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) | Kimball, *The Data Warehouse Toolkit* — ver [`90-bibliografia.md`](90-bibliografia.md) |
| **Lógica booleana: E, OU, NÃO, ordem de precedência** | Filtros, RLS e `CALCULATE` são álgebra booleana disfarçada | Qualquer material de lógica básica |
| **Noção de banco de dados relacional: chave primária, chave estrangeira** | Relacionamentos no modelo | [`../postgresql/00-MAPA.md`](../postgresql/00-MAPA.md) desta pasta |
| **Git básico: commit, branch, merge** | Só a partir do nível avançado ([`25-ciclo-de-vida-e-devops.md`](25-ciclo-de-vida-e-devops.md)) | [`../commits-assinados/00-MAPA.md`](../commits-assinados/00-MAPA.md) tem a base de Git |
| **Python ou R** | Opcional. Serve para visuais customizados e para o script de dados do projeto-modelo | Não é necessário para o curso |
| **Inglês de leitura** | Documentação oficial, mensagens de erro, 90% das respostas de fórum | Inevitável na carreira |

**Opinião do autor:** se você só tiver tempo para **um** pré-requisito além do básico,
escolha **SQL**. Não porque você vá escrever SQL no Power BI (às vezes vai), mas porque
SQL treina o raciocínio de conjuntos — "eu não manipulo uma linha, eu descrevo um filtro
sobre um conjunto". Esse é exatamente o raciocínio que DAX exige, e é o que falta em quem
vem só do Excel.

### 1.3 O que atrapalha (sim, existe)

- **Excel avançado demais, sem nada de banco de dados.** Quem domina `PROCV` aninhado e
  macros tende a tentar reproduzir isso no Power BI com colunas calculadas. Funciona, é
  lento, e não escala. Você vai precisar *desaprender* a instintiva vontade de "criar mais
  uma coluna ao lado".
- **Experiência com ferramentas de "dashboard" puramente visuais.** Elas ensinam que BI é
  desenhar. Não é.

---

## 2. Ambiente: o que você precisa ter

### 2.1 Requisitos oficiais mínimos do Power BI Desktop

Da documentação oficial da Microsoft, consultada em 14/08/2026:

| Item | Mínimo oficial | O que eu recomendo de verdade |
|---|---|---|
| Sistema operacional | Windows 10 ou Windows Server 2016+ | **Windows 11 x64**. Em Windows on ARM, exige a atualização cumulativa 2025-09 (KB5065789) |
| Arquitetura | **64 bits obrigatório** — a versão de 32 bits foi descontinuada | — |
| .NET | .NET Framework 4.7.2 ou superior | Já vem no Windows 10/11 atualizado |
| Navegador | Microsoft Edge (Internet Explorer não é mais suportado) | — |
| WebView2 | Necessário; normalmente instalado junto | Se faltar, instale à parte (ver [`03`](03-instalacao.md)) |
| Memória RAM | 2 GB disponíveis; 4 GB recomendado | **16 GB.** Com 8 GB você trabalha; com 16 GB você trabalha sem raiva. Modelos grandes pedem 32 GB |
| Processador | 1 GHz x64 ou melhor | Qualquer CPU dos últimos 6 anos. Power BI usa múltiplos núcleos na atualização e na consulta |
| Vídeo | **1440×900 ou 1600×900 (16:9)** no mínimo | Resoluções menores (1024×768, 1280×800) **não são suportadas** — alguns diálogos ficam fora da tela |
| Escala de exibição | 100% | Acima de 100%, certos diálogos ficam inacessíveis. Problema real, ver [`03`](03-instalacao.md) |
| Disco | ~1 GB para o programa | **20 GB livres.** Cache, arquivos `.pbix`, versões temporárias e a pasta `AnalysisServicesWorkspaces` crescem |

**O item que mais causa dor no mundo real é a RAM.** O modelo inteiro é carregado em
memória durante a edição, e o processo `msmdsrv.exe` (o motor Analysis Services embutido)
pode consumir vários GB. Ver [`21-vertipaq-por-dentro.md`](21-vertipaq-por-dentro.md).

### 2.2 O elefante na sala: macOS e Linux

**Não existe Power BI Desktop para macOS nem para Linux, e não há anúncio de roadmap**
(confirmado em 14/08/2026). Isso não é um esquecimento: o Desktop depende do motor
Analysis Services em processo e de componentes Windows.

Suas opções reais, em ordem de qualidade:

| Opção | Custa | Qualidade | Observação |
|---|---|---|---|
| Windows em máquina virtual (Parallels em Apple Silicon, VMware Fusion, UTM) | Licença Windows + Parallels | Boa | Melhor caminho no Mac. Windows 11 ARM roda o Desktop x64 por emulação |
| Windows 365 / Azure Virtual Desktop | Assinatura mensal | Boa | **Oficialmente suportado** pela Microsoft, ao contrário de Citrix |
| Dual boot / máquina Windows separada | Hardware | Ótima | Óbvia e ignorada |
| Só o Power BI Service no navegador | Grátis/licença | Limitada | Dá para editar relatórios e até modelar na web (cresceu muito em 2025–2026), mas não substitui o Desktop |
| Wine / CrossOver | — | Ruim | Funciona parcialmente e quebra a cada atualização. Não use para trabalho |

**Importante:** rodar o Power BI Desktop como aplicativo virtualizado publicado (Citrix
XenApp e similares) **não é suportado**. Azure Virtual Desktop e Windows 365, sim.

### 2.3 Contas e serviços

| Item | Obrigatório? | Custa? |
|---|---|---|
| Conta Microsoft pessoal (`@outlook.com`, `@gmail.com`) | Para usar o Desktop offline: não | — |
| **Conta corporativa/escolar (Microsoft Entra ID)** | **Sim, para publicar no Service** | Depende |
| Licença Power BI Pro | Para compartilhar com outra pessoa | US$ 14/usuário/mês |
| Cartão de crédito | **Não** para o Desktop nem para a conta gratuita | — |

**Armadilha número 1 do iniciante:** o Power BI Service **não aceita contas pessoais**.
Se você tem só `@gmail.com`, não consegue publicar. Saídas:

1. Usar o e-mail corporativo do trabalho (se a empresa permitir);
2. Criar um **Microsoft 365 Developer Program** ou uma **avaliação de 60 dias** do
   Microsoft 365 Business (exige domínio e, em alguns casos, cartão);
3. Registrar um domínio barato (~R$ 40/ano) e criar um locatário próprio — o que muitos
   analistas fazem para ter um laboratório pessoal.

Detalhes em [`03-instalacao.md`](03-instalacao.md) §9 e em [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

### 2.4 Dados para praticar

Você não precisa de dados da sua empresa (e provavelmente não deveria usá-los para
aprender — ver [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md)).

| Fonte | O que é | Link |
|---|---|---|
| **O projeto-modelo deste curso** | Distribuidora de tintas industriais, 3 anos, ~180 mil linhas, com defeitos plantados de propósito | [`07-projeto-modelo/`](07-projeto-modelo/README.md) |
| Contoso / AdventureWorks | Bases de exemplo clássicas da Microsoft | Microsoft Learn |
| Dados abertos do governo brasileiro | Reais, sujos, ótimos para treinar Power Query | `dados.gov.br` |
| Kaggle | Milhares de conjuntos, geralmente limpos demais | `kaggle.com/datasets` |

**Recomendação:** use o projeto-modelo. Dados limpos demais ensinam mal — eles escondem
exatamente a parte difícil do ofício.

---

## 3. Tempo realista até cada nível

Os números abaixo são o que eu observo em pessoas reais, estudando com regularidade e
com um problema real para resolver. Se você estudar sem um problema real, multiplique
tudo por dois e espere esquecer metade.

| Nível | O que você consegue fazer | Horas de estudo | Prazo típico |
|---|---|---|---|
| **Sobrevivência** | Conectar um Excel, fazer 5 gráficos, publicar | 8–12 h | 1 fim de semana |
| **Produtivo básico** | Power Query decente, esquema estrela simples, 20 medidas, relatório de 3 páginas que outra pessoa usa | 60–80 h | 6–10 semanas |
| **Analista de BI** | Contexto de avaliação dominado, `CALCULATE` sem medo, inteligência de tempo, RLS, atualização agendada, diagnóstico de lentidão | 250–350 h | 6–12 meses |
| **Sênior / engenheiro de análise** | Modelos compostos, DirectQuery/Direct Lake, otimização com DAX Studio, PBIP+Git+CI/CD, governança de locatário | 800–1.200 h | 2–4 anos |
| **Fronteira** | Contribui com a comunidade, entende o motor a ponto de prever plano de consulta, publica padrões | vários milhares | 5+ anos |

### Marcos honestos

- **A primeira semana é enganosamente fácil.** Arrastar campos funciona. Você vai achar
  que dominou. Isso dura até a primeira medida que devolve o número errado.
- **A parede é o contexto de avaliação.** Quase todo mundo empaca quando `CALCULATE` com
  `FILTER` produz resultado inesperado. Isso costuma acontecer entre a 40ª e a 80ª hora.
  Não é você; é o assunto. É por isso que [`16`](16-dax-contexto-de-avaliacao.md) é um
  arquivo inteiro em vez de uma seção.
- **A segunda parede é desempenho.** Aparece quando seu modelo passa de ~10 milhões de
  linhas ou o relatório passa de 5 segundos. Aí você descobre que precisa entender o motor.
- **A terceira é governança.** Aparece quando o relatório vira crítico e alguém pergunta
  quem pode ver o quê, e quem mudou aquela medida.

### Quanto tempo até a certificação PL-300?

Para quem já é produtivo básico: **60 a 100 horas** de estudo dirigido. Para quem parte do
zero: 250 a 400 horas. A PL-300 cobre preparar, modelar, visualizar e gerenciar/proteger.
Ver [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md).

---

## 4. Rota de resgate: o que fazer se faltar um pré-requisito

### "Não tenho Windows"
1. **Hoje:** crie conta gratuita e use o **Power BI Service no navegador** — dá para
   importar um CSV, criar um modelo e fazer relatórios simples. Você aprende conceitos.
2. **Esta semana:** decida entre máquina virtual (Parallels/VMware/UTM) ou Windows 365.
3. **Enquanto isso:** estude Power Query e DAX *teoricamente* com este material — a maior
   parte do que é difícil não depende de clicar.

### "Não sei nada de banco de dados / SQL"
Não bloqueie. Comece pelo Power BI com arquivos Excel/CSV e, **em paralelo**, faça as
seções 12 a 14 de [`../sql/`](../sql/00-MAPA.md) (SELECT, junções, agregação). Duas
semanas de SQL básico dobram o rendimento no Power BI.

### "Meu computador tem 8 GB de RAM"
Funciona. Precauções:
- Trabalhe com **amostras** (filtre a origem para 1 ano) enquanto constrói o modelo;
- Feche o navegador antes de abrir o Desktop (sim, é isso mesmo);
- Desative "Detecção automática de data/hora" nas opções — ela cria uma tabela de datas
  oculta para **cada** coluna de data do modelo e é o maior desperdício de memória do
  Power BI (ver [`75-armadilhas.md`](75-armadilhas.md), armadilha nº 3).

### "Não tenho conta corporativa para publicar"
Faça todo o curso no Desktop. Publicar é 5% do trabalho e 100% do que exige conta. Quando
conseguir a conta, os capítulos [`23`](23-servico-colaboracao-e-atualizacao.md) e
[`24`](24-seguranca-e-governanca.md) te esperam.

### "Não tenho um problema real para resolver"
Este é o pré-requisito mais subestimado. Invente um que te interessa: suas finanças
pessoais, o desempenho do seu time, o consumo de energia da sua casa, os dados abertos da
sua cidade. Ferramenta sem problema não gruda.

### "Não tenho tempo"
30 minutos por dia, cinco dias por semana, com um problema real, batem 8 horas de sábado
por mês. BI é uma habilidade que se constrói por repetição espaçada, não por maratona.

---

## 5. Checklist antes de ir para a instalação

- [ ] Tenho acesso a uma máquina Windows 10/11 de 64 bits (própria, VM ou nuvem).
- [ ] Tenho pelo menos 8 GB de RAM (idealmente 16 GB) e 20 GB livres em disco.
- [ ] Minha resolução de tela é ao menos 1440×900 e a escala está em 100%.
- [ ] Sei se vou publicar (então preciso de conta corporativa) ou só usar o Desktop.
- [ ] Tenho um conjunto de dados para praticar — de preferência o do projeto-modelo.
- [ ] Sei o que é uma tabela, uma linha, uma coluna e um percentual.
- [ ] Tenho um problema real em mente que quero resolver.

Se marcou tudo: [`03-instalacao.md`](03-instalacao.md).
Se faltou algo do ambiente: o `03` também trata dos contornos.

---

## 6. Autoteste

1. Quais são os quatro pré-requisitos de conhecimento realmente indispensáveis?
2. Por que SQL é o pré-requisito opcional com melhor retorno?
3. Qual a resolução mínima de tela suportada, e o que acontece abaixo dela?
4. Você tem um MacBook. Cite três caminhos viáveis, e diga qual é oficialmente suportado
   pela Microsoft.
5. Por que uma conta `@gmail.com` não serve para publicar no Power BI Service?
6. Quantas horas, realisticamente, separam "zero" de "analista de BI"?
7. Qual configuração deve ser desativada primeiro numa máquina com pouca RAM, e por quê?
8. Qual é o pré-requisito que não aparece em nenhuma lista oficial e que, na minha opinião,
   decide se você vai aprender ou desistir?

---

**Próximo:** [`03-instalacao.md`](03-instalacao.md) — o manual de campo.

---

*Fontes consultadas em 14/08/2026: [Microsoft Learn — Download Power BI Desktop (requisitos mínimos, virtualização, KB5065789)](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop); [Microsoft Certified: Power BI Data Analyst Associate](https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/).*
