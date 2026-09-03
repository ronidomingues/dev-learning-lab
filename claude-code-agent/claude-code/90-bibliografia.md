# 90 · Bibliografia comentada

> **Nível:** todos · **Atualizado em:** 13/08/2026
> **Regra desta lista:** nada inventado. Onde não tenho certeza de edição ou ISBN, cito só
> autor e título. Livro **especificamente sobre Claude Code** praticamente não existe em
> forma consolidada — a ferramenta é de 2025 e muda semanalmente. Por isso esta bibliografia
> é, deliberadamente, sobre **o que sustenta o uso profissional de um agente**.

---

## Aviso metodológico

Um livro leva de 12 a 24 meses entre escrita e publicação. Claude Code muda de superfície em
semanas. **Qualquer livro sobre "como usar o Claude Code" nasce desatualizado nos detalhes.**

O que envelhece bem: engenharia de software, testes, projeto de código, teoria da computação.
Justamente o que determina se você extrai 10× ou 1,2× ([`25`](25-o-oficio-do-profissional.md)).

Para a ferramenta em si, a fonte é a documentação oficial ([`95`](95-referencias.md)).

---

## 1. O que sustenta o uso profissional

### Testes — o pré-requisito nº 1

**Kent Beck — *Test-Driven Development: By Example*.** Addison-Wesley, 2002.
Nível: iniciante–intermediário. Edição em português: *TDD: Desenvolvimento Guiado por Testes*
(Bookman). **Por que agora:** o laço "escreva o teste → veja falhar → faça passar" é
exatamente o laço que um agente executa bem. Quem entende TDD sabe montar oráculo — e
oráculo é a diferença entre delegar trabalho e delegar a ilusão de trabalho. Envelheceu?
Os exemplos, sim; a ideia central, nada.

**Michael Feathers — *Working Effectively with Legacy Code*.** Prentice Hall, 2004.
Nível: intermediário–avançado. Edição em português: *Trabalho Eficaz com Código Legado*
(Bookman). **Por que agora:** define "código legado" como código sem testes e ensina a
introduzir testes em código que não os tem. É exatamente o preparo que falta na maioria dos
repositórios onde agentes decepcionam. **Meu voto de livro mais subestimado desta lista.**

**Neste próprio repositório:** [`../testes-automatizados/00-MAPA.md`](../testes-automatizados/00-MAPA.md)
— curso completo, em português, com projeto executável em Python e JavaScript.

### Projeto de código — o que torna um repositório navegável por agente

**Martin Fowler — *Refactoring: Improving the Design of Existing Code*.** 2ª ed.,
Addison-Wesley, 2018. Nível: intermediário. Há edição em português da 1ª edição.
**Por que agora:** o catálogo de refatorações descreve transformações **mecânicas e
verificáveis** — a categoria em que agentes são mais fortes. Saber nomear a refatoração que
você quer melhora drasticamente o pedido. A 2ª edição usa JavaScript.

**Robert C. Martin — *Clean Code*.** Prentice Hall, 2008. Nível: iniciante.
Edição em português: *Código Limpo* (Alta Books). **Ressalva honesta:** livro
controverso — parte da comunidade considera várias recomendações datadas ou dogmáticas.
Leia pelo vocabulário compartilhado (nomes, funções pequenas, efeitos colaterais), não como
escritura. **[opinião, e nada consensual]**

**Titus Winters, Tom Manshreck, Hyrum Wright — *Software Engineering at Google*.**
O'Reilly, 2020. Nível: intermediário–avançado. **Por que agora:** trata do que muda quando
código vive por décadas e é mantido por muita gente — que é a lente correta para pensar
código gerado em volume. O capítulo sobre revisão é o mais relevante para o gargalo descrito
no [`25`](25-o-oficio-do-profissional.md).

### Fundamentos que não envelhecem

**Frederick P. Brooks Jr. — *The Mythical Man-Month*.** Ed. de aniversário, Addison-Wesley,
1995 (original de 1975). Edição em português: *O Mítico Homem-Mês*. **Por que agora:** o
ensaio *No Silver Bullet* distingue complexidade **essencial** de **acidental** e argumenta
que nenhuma tecnologia isolada dará ganho de ordem de grandeza. Cada onda de IA reacende o
debate; ler o argumento original protege contra os dois exageros — o entusiasta e o cético.

**David Thomas e Andrew Hunt — *The Pragmatic Programmer*.** Ed. de 20 anos,
Addison-Wesley, 2019. Edição em português: *O Programador Pragmático*.
**Por que agora:** automação, "não se repita", tratar o próprio processo como objeto de
melhoria. É o espírito do [`25`](25-o-oficio-do-profissional.md), escrito décadas antes.

---

## 2. Fundamentos técnicos de LLM

**Jurafsky & Martin — *Speech and Language Processing*, 3ª edição.**
**Gratuito e legal**, dos autores: https://web.stanford.edu/~jurafsky/slp3/
Nível: intermediário–avançado. O livro-texto do campo. Para este curso, os capítulos de
transformadores e de modelos de linguagem grandes bastam.

**Sebastian Raschka — *Build a Large Language Model (From Scratch)*.** Manning, 2024.
Nível: intermediário. **Por que agora:** implementar um transformador pequeno derruba
definitivamente a intuição mágica. Se você entender de onde vem o custo $O(n^2)$ na prática,
o [`60`](60-teoria-avancada.md) deixa de ser abstrato.

**Chip Huyen — *AI Engineering*.** O'Reilly, 2025. Nível: intermediário.
**Por que agora:** trata de construir sistemas **em torno** de modelos — avaliação, custo,
latência, dados. É a disciplina que o [`26`](26-times-e-escala.md) exige em escala.

> **Nota de precisão:** não confirmei a edição impressa e o ISBN de *AI Engineering* nesta
> pesquisa. Cito autora e título; confira antes de comprar.

**Não confie em livro de 2023–2024 para números.** Preços, janelas de contexto e capacidades
mudaram por ordens de grandeza. Leia-os por conceito.

---

## 3. Teoria — para o [`60`](60-teoria-avancada.md)

**Michael Sipser — *Introduction to the Theory of Computation*.** 3ª ed., Cengage, 2012.
Nível: avançado. Edição em português: *Introdução à Teoria da Computação* (Cengage).
**Por que agora:** decidibilidade, problema da parada, teorema de Rice. É o que sustenta a
afirmação de que nenhum agente pode **garantir** correção — não por limitação de modelo, mas
por teorema.

**Christopher Bishop — *Pattern Recognition and Machine Learning*.** Springer, 2006.
Nível: avançado. Clássico e ainda válido para os fundamentos probabilísticos. Não cobre
transformadores (é anterior).

---

## 4. Segurança

**OWASP — *Top 10 for Large Language Model Applications*.** **Gratuito**, em
[owasp.org](https://owasp.org/). **Por que agora:** injeção de prompt é o item nº 1 da lista.
Referência curta e direta para o [`24`](24-seguranca.md).

**Neste repositório:** [`../ethical-hacking/00-MAPA.md`](../ethical-hacking/00-MAPA.md) —
inclui a fronteira de IA ofensiva e OWASP Top 10:2025.

---

## 5. Sobre trabalho e organização

**Nicole Forsgren, Jez Humble, Gene Kim — *Accelerate*.** IT Revolution, 2018.
Nível: intermediário. Edição em português pela Alta Books.
**Por que agora:** as quatro métricas DORA (frequência de entrega, lead time, taxa de falha,
tempo de restauração) são muito melhores para avaliar adoção de agente do que "linhas
aceitas" ([`26`](26-times-e-escala.md)). Baseado em pesquisa, não em anedota.

**Camille Fournier — *The Manager's Path*.** O'Reilly, 2017.
**Por que agora:** para quem vai liderar adoção. Nada sobre IA; tudo sobre a parte humana,
que é onde adoções falham.

---

## 6. Leituras curtas que valem mais que muitos livros

| Texto | Onde | Por quê |
|---|---|---|
| **Documentação oficial do Claude Code** | [code.claude.com/docs](https://code.claude.com/docs) | Gratuita, atualizada, densa. É o "livro" desta ferramenta |
| **Especificação do MCP** | [modelcontextprotocol.io](https://modelcontextprotocol.io) | Curta e bem escrita. Entender o protocolo muda como você usa |
| **Dijkstra, *Notes on Structured Programming* (1970)** | domínio público | "Testes mostram a presença de bugs, nunca a ausência" |
| **Brooks, *No Silver Bullet* (1986)** | ensaio, incluído no *Mythical Man-Month* | Complexidade essencial × acidental |
| **Papers do [`95`](95-referencias.md)** | arXiv, gratuitos | *Attention*, *Lost in the Middle*, *ReAct*, *SWE-bench* |

---

## 7. Trilha por perfil

**Programador que quer ficar bom rápido:**
Beck (*TDD*) → Feathers (*Legacy Code*) → documentação oficial → este curso, [`25`](25-o-oficio-do-profissional.md).

**Quem lidera adoção num time:**
Forsgren (*Accelerate*) → Winters (*SE at Google*, cap. de revisão) → este curso, [`26`](26-times-e-escala.md).

**Quem quer entender por dentro:**
Jurafsky & Martin (grátis) → Raschka → Sipser → este curso, [`60`](60-teoria-avancada.md).

**Quem se preocupa com segurança:**
OWASP LLM Top 10 → este curso, [`24`](24-seguranca.md) → [`../ethical-hacking/`](../ethical-hacking/00-MAPA.md).

---

## 8. O que **não** ler

**[opinião]**

- Livros de "engenharia de prompt" com fórmulas mágicas. O que funciona é dizer com clareza
  o que você quer e como se verifica — isso não enche um livro.
- Qualquer livro de 2023–2024 pelos **números**: preços, janelas e capacidades mudaram por
  ordens de grandeza.
- Livros de "IA vai mudar tudo" sem código. Custam tempo e não mudam o que você faz na
  segunda-feira.

---

## Autoteste

1. Por que praticamente não existe livro bom **especificamente** sobre Claude Code?
2. Qual livro desta lista é o mais diretamente ligado ao Pilar 1 do [`25`](25-o-oficio-do-profissional.md), e por quê?
3. Qual é o livro gratuito e legal para fundamentos de LLM, e onde encontrá-lo?
4. Que argumento de *No Silver Bullet* é relevante para o debate atual sobre agentes?
5. Que ressalva este arquivo faz sobre *Clean Code*, e por que ela está marcada como opinião?
6. Por que as métricas DORA são melhores que "linhas aceitas" para medir adoção?
7. Cite um caso em que este arquivo admite não ter confirmado a edição. Por que isso importa?
