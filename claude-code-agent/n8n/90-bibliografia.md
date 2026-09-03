# 90 · Bibliografia comentada

`Nível: todos` · **Pesquisado na web em 01/09/2026**

---

## Aviso, e ele é o mais importante deste arquivo

> **Não existe, em 01/09/2026, um livro de referência sobre n8n publicado por
> editora técnica reconhecida.**

O que existe na Amazon é uma dezena de títulos **autopublicados** (KDP), lançados
entre 2025 e 2026, com títulos intercambiáveis do tipo "Mastering n8n",
"n8n Automation Mastery", "Automate Everything with n8n". Alguns exemplos reais,
com autor e identificador, para você reconhecer a categoria:

| Título | Autor | Publicação | ISBN-13 (KDP) |
|---|---|---|---|
| *n8n Automation Mastery* | Amjid Ali | mar/2025 | 979-8314198018 |
| *Automating Workflows with n8n and AI* | Darryl Jeffery | abr/2025 | 979-8316657629 |
| *Mastering n8n* | Hawke Nexon | mai/2025 | 979-8282362138 |
| *Practical n8n Project Book* | Jordan Carter | jul/2025 | 979-8293721658 |
| *Automate Everything with n8n* | Akshay Pachaar | out/2025 | 979-8268753080 |
| *Mastering n8n Workflows* | Orion Vera | mar/2026 | 979-8250456487 |

**Minha recomendação profissional:** não compre nenhum sem folhear a amostra.
Três razões objetivas:

1. **Envelhecem em semanas.** O n8n lança uma versão menor quase toda semana, e o
   3.0 (out/2026) remove nós, o AI Agent v1 e a instalação por npm. Um livro de 2025
   já ensina coisas que deixam de existir.
2. **A documentação oficial é melhor, gratuita e atualizada.** Está em
   `docs.n8n.io`, inclusive em Markdown limpo (`.md` em qualquer URL).
3. **Nenhum passou por revisão técnica editorial**, e isso é perceptível na amostra
   de vários deles.

**Onde investir o seu dinheiro de livro:** nos fundamentos que **não** envelhecem —
integração, sistemas distribuídos e confiabilidade. É o que está abaixo, e é o que
separa quem monta fluxo de quem projeta automação.

---

## 1. Integração — a base intelectual do que o n8n faz

### ⭐ Hohpe, G. & Woolf, B. — *Enterprise Integration Patterns*
Addison-Wesley, 2003. ISBN 978-0321200686.
**Nível:** intermediário → avançado. **Envelheceu?** A tecnologia sim, os padrões não.

O livro que nomeou o que você faz no n8n sem saber o nome: *Message Router*
(seu Switch), *Splitter* (Split Out), *Aggregator* (Aggregate), *Content Enricher*,
*Dead Letter Channel*, *Idempotent Receiver*. Ler este livro é ganhar vocabulário
para pensar — e para conversar com arquitetos.

**Gratuito e legal:** o catálogo de padrões está aberto em
<https://www.enterpriseintegrationpatterns.com/patterns/messaging/>. Comece por ali;
compre o livro se o catálogo te fisgar.

### Fowler, M. — *Patterns of Enterprise Application Architecture*
Addison-Wesley, 2002. ISBN 978-0321127426.
**Nível:** intermediário. Datado em tecnologia, sólido em conceito. O catálogo
resumido é aberto em <https://martinfowler.com/eaaCatalog/>.

---

## 2. Sistemas distribuídos — por que "exatamente uma vez" não existe

### ⭐⭐ Kleppmann, M. — *Designing Data-Intensive Applications*
O'Reilly, 2017. ISBN 978-1449373320.
**Nível:** intermediário → avançado. **Envelheceu?** Não. É o melhor livro de
sistemas da última década.

Se você lê **um** livro desta lista, leia este. Os capítulos sobre replicação,
consistência, transações e processamento de fluxos explicam formalmente tudo o que
o arquivo [18](18-erros-e-confiabilidade.md) diz na prática: por que *at-least-once*
mais idempotência é a resposta, e por que *exactly-once* é conversa de vendedor.

*(Há edição em português publicada no Brasil; a tradução circula com boa reputação,
mas eu li em inglês e não posso avaliá-la em primeira mão. Confira uma amostra antes.)*

### Tanenbaum, A. & Van Steen, M. — *Distributed Systems*
4ª edição, 2023 (publicação dos autores).
**Nível:** avançado, com viés acadêmico.
**Legalmente gratuito:** os autores disponibilizam o PDF em
<https://www.distributed-systems.net/index.php/books/ds4/>.
Livro-texto clássico. Use como referência de consulta, não de leitura linear.

---

## 3. Confiabilidade e operação

### ⭐ Nygard, M. — *Release It! Design and Deploy Production-Ready Software*
Pragmatic Bookshelf, 2ª edição, 2018. ISBN 978-1680502398.
**Nível:** intermediário. **Envelheceu?** Não.

O livro dos padrões de estabilidade: *Circuit Breaker*, *Bulkhead*, *Timeout*,
*Fail Fast*, *Steady State*. Todo o arquivo [18](18-erros-e-confiabilidade.md) e a
seção de disjuntor manual do [15](15-fluxo-de-controle.md) vêm daqui. É também o
livro que ensina a pensar em *como isto vai falhar* antes de *como isto vai funcionar*.

### ⭐ Beyer, B. et al. (org.) — *Site Reliability Engineering*
O'Reilly / Google, 2016. ISBN 978-1491929124.
**Legalmente gratuito, na íntegra:** <https://sre.google/books/>.
**Nível:** intermediário. Leia os capítulos sobre monitoramento, alerta e trabalho
manual. O conceito de "alerta acionável" é diretamente aplicável ao seu Error Workflow.

### Newman, S. — *Building Microservices*
O'Reilly, 2ª edição, 2021. ISBN 978-1492034025.
**Nível:** intermediário. Útil pelos capítulos de integração, versionamento de
contrato e sagas — o padrão para "gravou no A, falhou no B", que o n8n não resolve
por você ([60](60-teoria-avancada.md)).

### Richardson, C. — *Microservices Patterns*
Manning, 2018. ISBN 978-1617294549.
**Nível:** intermediário → avançado. O melhor tratamento prático de **saga** e de
**outbox transacional** — os dois padrões que resolvem consistência entre sistemas
sem transação distribuída. Catálogo aberto em <https://microservices.io/patterns/>.

---

## 4. Fundamentos de programação, para quem vem de fora

### Flanagan, D. — *JavaScript: The Definitive Guide*
O'Reilly, 7ª edição, 2020. ISBN 978-1491952023.
**Nível:** iniciante → avançado. Referência para o node Code e as expressões.
**Alternativa gratuita e melhor para aprender:** <https://javascript.info/> (tem
tradução para português, de boa qualidade).

### Beaulieu, A. — *Learning SQL*
O'Reilly, 3ª edição, 2020. ISBN 978-1492057611.
**Nível:** iniciante. Quase todo fluxo sério toca banco.
**Alternativa gratuita:** <https://sqlbolt.com/> e a pasta
[`postgresql/`](../postgresql/00-MAPA.md) deste repositório.

---

## 5. Papers e textos fundadores (para o arquivo [60](60-teoria-avancada.md))

| Trabalho | Autor, ano | Por que ler |
|---|---|---|
| *The Semantics of a Simple Language for Parallel Programming* | Kahn, G., 1974 | Define as *Kahn Process Networks*, a formalização de fluxo de dados com canais |
| *First Version of a Data Flow Procedure Language* | Dennis, J., 1974 | Origem do paradigma de dataflow |
| *Why and Where: A Characterization of Data Provenance* | Buneman, Khanna & Tan, ICDT 2001 | A teoria por trás do que o `pairedItem` implementa |
| *Time, Clocks, and the Ordering of Events in a Distributed System* | Lamport, L., 1978 | Por que ordenar eventos entre sistemas é difícil |
| *Notes on Distributed Databases* (o problema dos dois generais) | Gray, J., 1978 | O argumento formal contra *exactly-once* |

---

## 6. Em português: o que existe

**Sobre n8n especificamente: nada de qualidade editorial, até 01/09/2026.**
O material em PT é vídeo, e está no arquivo [85](85-cursos-e-certificacoes.md).

Sobre os fundamentos, em português:

- **javascript.info em português** — <https://javascript.info/> (gratuito, excelente).
- **Documentação do PostgreSQL em português** — parcial, mas útil.
- Este repositório: [`apis/`](../apis/00-MAPA.md), [`docker/`](../docker/00-MAPA.md),
  [`postgresql/`](../postgresql/00-MAPA.md), [`jwt/`](../jwt/00-MAPA.md),
  [`tls/`](../tls/00-MAPA.md).

---

## 7. Ordem de leitura sugerida

| Se você é… | Leia nesta ordem |
|---|---|
| **Iniciante total** | javascript.info → catálogo aberto do EIP → *Learning SQL* |
| **Dev que vai usar n8n** | *Release It!* → *Designing Data-Intensive Applications* → *Enterprise Integration Patterns* |
| **Quem vai operar em produção** | *Site Reliability Engineering* (gratuito) → *Release It!* → cap. 5–9 do Kleppmann |
| **Quem quer profundidade teórica** | Kleppmann → Tanenbaum (gratuito) → os papers da seção 5 |

---

## Autoteste

1. Por que não recomendo os livros de n8n disponíveis hoje? Cite três razões.
2. Qual livro nomeia os padrões que você já usa no n8n sem saber o nome?
3. Qual é o único livro desta lista que eu leria se pudesse ler só um, e por quê?
4. Cite três livros desta lista que são **legalmente gratuitos** e onde obtê-los.
5. Qual livro trata dos padrões de estabilidade (Circuit Breaker, Bulkhead)?
6. Onde estudar o padrão *saga*, e que problema do n8n ele resolve?
7. Qual paper de 1974 formaliza o modelo de fluxo de dados?
8. Existe livro bom de n8n em português? Qual a alternativa?

---

*Nenhum livro, ISBN ou link deste arquivo foi inventado: todos foram verificados na
web em 01/09/2026. Onde eu não tinha certeza (qualidade de tradução, por exemplo),
está dito explicitamente.*

*Anterior: [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) · Próximo: [95-referencias.md](95-referencias.md)*
