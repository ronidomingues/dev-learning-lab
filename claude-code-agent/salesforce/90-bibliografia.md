# 90 · Bibliografia comentada

`Nível: todos` · `Verificado em 11/08/2026`

Regra deste arquivo: **nada inventado**. Onde eu não tenho certeza da edição ou do ISBN,
cito apenas autor e título e digo que é aproximado. Livro de Salesforce envelhece rápido —
a coluna "envelheceu?" é a mais importante da tabela.

---

## 1. Aviso sobre livros de Salesforce

Antes da lista, três verdades desconfortáveis:

1. **A documentação oficial é melhor que a maioria dos livros**, e é gratuita e atualizada
   três vezes por ano. Livro de Salesforce compete com um alvo móvel.
2. **Livros de preparação para certificação envelhecem em ~2 anos.** A prova é revisada a
   cada release. Compre a edição mais recente ou não compre.
3. **O que envelhece devagar** é o que trata de **arquitetura, padrões e princípios**.
   É aí que o livro ganha da documentação, e é aí que vale investir dinheiro.

---

## 2. Arquitetura e padrões — o que vale comprar

### **Salesforce Platform Enterprise Architecture** — Andrew Fawcett
*Packt · 4ª edição (2023)*

**Nível:** avançado. **Envelheceu?** Os padrões, não. Alguns detalhes de API, sim.

O livro mais importante da lista. Apresenta os *Enterprise Patterns* (Domain, Selector,
Service, Unit of Work) que se tornaram o vocabulário padrão do ecossistema para código
Apex organizado — a base da biblioteca `fflib-apex-common`.

**Leia se:** você vai manter uma base de Apex que passa de alguns milhares de linhas.
**Não leia se:** você está começando. Os padrões parecem burocracia excessiva até você
sentir a dor que eles resolvem.

### **Mastering Apex Programming** — Paul Battisson
*Packt · 2ª edição (novembro de 2023)*

**Nível:** intermediário → avançado. **Envelheceu?** Pouco; a 2ª edição foi reestruturada e
acrescentou cinco capítulos, incluindo DataWeave em Apex e uso combinado de Flow com Apex.

Cobre assíncrono, depuração, performance, tratamento de erro e testes com profundidade que
a documentação não tem. É o melhor livro *sobre a linguagem em uso real* que conheço.

### **Advanced Apex Programming in Salesforce** — Dan Appleman
*Desert Isle Group · várias edições*

**Nível:** avançado. **Envelheceu?** O conteúdo conceitual, não; verifique a edição.

Começa onde a documentação da Salesforce termina. É especialmente forte em: como pensar
sobre limites, arquitetura de triggers, e as decisões de projeto por trás do que a
plataforma permite. Apesar do subtítulo indicar público de Java/C#, é útil a qualquer
desenvolvedor Apex experiente.

> **Nota de honestidade:** este livro teve várias edições ao longo dos anos e eu não tenho
> certeza de qual é a mais recente em 2026. Verifique antes de comprar.

### **The Force.com Multitenant Architecture** — Salesforce / O'Reilly
*O'Reilly · 2008*

**Nível:** pesquisa. **Envelheceu?** Nos detalhes, muito. Nos princípios, nada.

Descrição da arquitetura interna: UDD, pivot tables, query optimizer. É a base do
[19-multitenancy-arquitetura.md](19-multitenancy-arquitetura.md). O conteúdo essencial
também está no **whitepaper gratuito**:
https://www.developerforce.com/media/ForcedotcomBookLibrary/Force.com_Multitenancy_WP_101508.pdf

**Leia o whitepaper primeiro.** Se ele te interessar, procure o livro.

---

## 3. Livros que não são de Salesforce, mas deveriam estar em toda estante

Estes envelhecem em décadas, não em anos. Na minha opinião, valem mais que qualquer livro
de certificação.

### **Designing Data-Intensive Applications** — Martin Kleppmann
*O'Reilly · 1ª edição (2017)* · *(há uma 2ª edição em preparação; confirme a disponibilidade)*

**Nível:** avançado. **Envelheceu?** Não.

Consistência, replicação, particionamento, transações distribuídas, idempotência,
processamento de streams. Tudo que explica **por que** a integração do
[06-exemplos.md](06-exemplos.md) §13 é assim. Se você só puder comprar um livro técnico
este ano, compre este.

### **Release It!** — Michael Nygard
*Pragmatic Bookshelf · 2ª edição (2018)*

**Nível:** intermediário → avançado. **Envelheceu?** Não.

Padrões de estabilidade: circuit breaker, bulkhead, timeout, backoff. É a fonte dos padrões
usados no exemplo de integração deste curso.

### **Refactoring** — Martin Fowler
*Addison-Wesley · 2ª edição (2018, exemplos em JavaScript)*

**Nível:** intermediário. **Envelheceu?** Não.

Apex é sintaticamente próximo de Java; os catálogos de refatoração se aplicam quase
integralmente. A 2ª edição usa JavaScript, o que também serve para LWC.

### **Patterns of Enterprise Application Architecture** — Martin Fowler
*Addison-Wesley · 2002*

**Nível:** avançado. **Envelheceu?** O vocabulário, não. Alguns padrões, sim.

É de onde vêm os nomes *Unit of Work*, *Data Mapper*, *Service Layer* que Fawcett adaptou
para Salesforce. Ler a fonte original ajuda a entender por que os padrões são assim.

---

## 4. Preparação para certificação

| Livro | Certificação | Comentário |
|---|---|---|
| *Salesforce Certified Administrator Study Guide* (vários autores/editoras) | Administrator | Muitos títulos concorrentes. **Verifique o ano de publicação** — anterior a 2024 já está defasado |
| *Salesforce Platform Developer I Certification Guide* (Packt) | PD I | Existe em edições sucessivas; confira a mais recente |
| *Salesforce Advanced Administrator Certification Guide* (Packt) | Advanced Admin | idem |

> **Recomendação franca:** **não compre livro de certificação.** O Trailhead cobre o
> conteúdo oficial de graça e está sempre atualizado; o *Exam Guide* oficial dá os pesos
> por seção; e simulados (Focus on Force) treinam o formato melhor que qualquer livro.
> Livro de certificação é o pior investimento da lista.
>
> Se ainda assim quiser um, o critério é: **publicado nos últimos 18 meses**, e que
> mencione Flow (não Process Builder) e `sf` (não `sfdx`).

---

## 5. Legalmente gratuitos

| Título | Onde | Nota |
|---|---|---|
| **The Force.com Multitenant Architecture** (whitepaper) | https://www.developerforce.com/media/ForcedotcomBookLibrary/Force.com_Multitenancy_WP_101508.pdf | a fonte primária sobre a arquitetura interna |
| **Apex Developer Guide** | https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/ | referência completa da linguagem; equivale a um livro |
| **Lightning Web Components Developer Guide** | https://developer.salesforce.com/docs/component-library/documentation/lwc | idem, para LWC |
| **SOQL and SOSL Reference** | https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/ | referência de consulta |
| **Salesforce Architects — guias e padrões** | https://architect.salesforce.com | guias oficiais de arquitetura, gratuitos e de boa qualidade |
| **Integration Patterns and Practices** | https://developer.salesforce.com/docs/atlas.en-us.integration_patterns_and_practices.meta/integration_patterns_and_practices/ | a fonte oficial dos padrões de integração |
| **Well-Architected Framework** (Salesforce) | https://architect.salesforce.com/well-architected | princípios de arquitetura; leitura curta e útil |

**Estes sete recursos, somados, cobrem mais conteúdo com mais atualidade do que qualquer
livro pago da lista.** Comece por eles.

---

## 6. Livros e materiais em português

O mercado editorial brasileiro **praticamente não publica sobre Salesforce**. Não conheço
um livro técnico de Salesforce em português do Brasil que eu possa recomendar com
segurança — e prefiro dizer isso a inventar um título.

**O que existe em português e vale:**
- **Trailhead em pt-BR** (§1 de [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md));
- documentação parcialmente traduzida em https://help.salesforce.com;
- conteúdo de comunidade no YouTube e no LinkedIn.

**Livros de fundamentos traduzidos que valem** (e que se aplicam a Salesforce):
- *Refatoração* — Martin Fowler (há edições em português)
- *Padrões de Projeto* — Gamma, Helm, Johnson, Vlissides (Bookman)

> Sobre traduções: em geral, edições brasileiras de livros técnicos da Bookman e da Novatec
> têm qualidade aceitável. Ainda assim, se você lê inglês com conforto, prefira o original —
> a terminologia técnica traduzida frequentemente diverge do que a comunidade usa no dia a dia.

---

## 7. Como escolher, em uma tabela

| Você quer | Leia |
|---|---|
| Aprender a plataforma do zero | **Trailhead**, não um livro |
| Passar numa certificação | Trailhead + Exam Guide + simulados |
| Organizar uma base grande de Apex | Fawcett, *Enterprise Architecture* |
| Dominar Apex de verdade | Battisson, *Mastering Apex Programming* |
| Entender por que a plataforma é assim | whitepaper de multitenancy + [19](19-multitenancy-arquitetura.md) |
| Fazer integração que não quebra | Kleppmann + Nygard + guia oficial de integração |
| Melhorar como programador em geral | Fowler, *Refactoring* |
| Referência para consultar | a documentação oficial, sempre |

---

## Autoteste

1. Por que a documentação oficial supera a maioria dos livros de Salesforce?
2. Qual livro você compraria para organizar uma base de Apex grande, e por quê?
3. Qual é o único livro da lista que você compraria mesmo trabalhando fora do Salesforce?
4. Por que livros de preparação para certificação são o pior investimento da lista?
5. Cite três recursos legalmente gratuitos que equivalem a livros.
6. Qual é a situação da bibliografia de Salesforce em português, e o que fazer a respeito?
7. Que critério usar para decidir se um livro de Salesforce ainda está atual?
