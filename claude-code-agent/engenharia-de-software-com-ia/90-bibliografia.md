# 90 · Bibliografia comentada

**Nível:** todos · **Verificado na web em: 20/08/2026**

> Edições e ISBNs conferidos na data acima. **Nada foi inventado.** Onde eu não
> tinha certeza de um dado, omiti o dado em vez de chutar.
>
> **Advertência que este assunto exige:** livro sobre IA em software envelhece
> em 12 a 24 meses. Os livros **específicos** desta lista são úteis pelo método,
> não pelas ferramentas que citam. Os **clássicos** são o oposto: envelhecem
> devagar e explicam por que as coisas são como são.

---

## Parte I · Específicos do assunto

### Os três que valem em 2026

**1. Osmani, Addy. *Beyond Vibe Coding: From Coder to AI-Era Developer*.
O'Reilly Media, 23/09/2025. 252 p. ISBN 979-8341634756.**

O melhor panorama disponível da transição de papel: de escrever código para
dirigir a escrita de código. O autor é engenheiro do Chrome no Google, o que dá
peso prático ao argumento.

**Nível:** intermediário. **Onde brilha:** nomear e organizar a mudança de
papel; tratar *vibe coding* como técnica com lugar definido, não como estilo de
vida. **Onde envelhece:** as ferramentas citadas. **Existe em português?** Não
localizei edição em PT-BR.

---

**2. Barbini, Uberto. *Process Over Magic: Beyond Vibe Coding — Faster, Smarter,
and Safer Coding with AI Assistants*. Pragmatic Bookshelf, 10/06/2026. 132 p.
ISBN 979-8888652008.**

O livro mais alinhado com a tese deste curso. O argumento central é o mesmo:
**usar IA bem depende de processo disciplinado, não de prompt esperto.** O autor
vem do TDD e do Extreme Programming, e isso se nota — o método é passos
pequenos, controlados, com verificação.

**Nível:** intermediário. **Onde brilha:** passos pequenos, *guardrails*,
experiência de projeto real, vídeos companheiros. **Onde é curto:** 132 páginas
— é um livro enxuto, não um tratado; não cobre segurança nem organização em
profundidade. **Existe em português?** Não localizei.

**Se você só for ler um livro específico, leia este.**

---

**3. Kim, Gene; Yegge, Steve. *Vibe Coding: Building Production-Grade Software
With GenAI, Chat, Agents, and Beyond*. IT Revolution, 2025. Prefácio de Dario
Amodei. ISBN 978-1966280026.**

O mais ambicioso e o mais polêmico. Gene Kim vem de *The Phoenix Project* e
*Accelerate*; Steve Yegge é uma voz conhecida e provocativa da indústria.
Prêmios: ouro no Axiom 2026 (Business Technology) e prata no IBPA Benjamin
Franklin 2026.

**Nível:** intermediário a avançado. **Onde brilha:** escala organizacional e o
que muda no processo de engenharia. **Onde eu discordo, e digo abertamente:** o
livro é notavelmente otimista sobre delegar confiança à IA — uma resenha de
*The Register* (21/10/2025) o resume como "confie na IA, diz o novo manifesto de
programação". Leia junto com a evidência do
[24-produtividade](24-produtividade-o-que-diz-a-evidencia.md) para calibrar.
**Existe em português?** Não localizei.

---

### Panorama anterior, ainda útil como referência

**4. Taulli, Tom. *AI-Assisted Programming: Better Planning, Coding, Testing,
and Deployment*. O'Reilly Media, 21/05/2024. 222 p. ISBN 978-1098164560.**

Cobre o ciclo inteiro — requisitos, planejamento, projeto, codificação,
depuração, teste, documentação — com ferramentas da época.

**Nível:** iniciante a intermediário. **Envelheceu?** **Sim, bastante.** É
anterior à era dos agentes: fala de Copilot, Tabnine, CodeWhisperer e do fluxo
de chat. Leia pelo enquadramento do ciclo, não pelas ferramentas. **Se você tem
tempo para um só livro específico, prefira o de Barbini.**

---

## Parte II · Clássicos que ficaram mais relevantes

Estes não falam de IA. Explicam por que o que estamos vivendo acontece.

**5. Brooks, Frederick P. Jr. *The Mythical Man-Month: Essays on Software
Engineering, Anniversary Edition*. Addison-Wesley, 1995. ISBN 978-0201835953.**

Contém *No Silver Bullet* (1986), com a distinção entre complexidade
**essencial** e **acidental**. É o melhor instrumento existente para avaliar
qualquer promessa de produtividade — inclusive as de 2026.

**Nível:** todos. **Envelheceu?** A parte técnica sim; os ensaios, não.
**Em português:** *O Mítico Homem-Mês*, Bookman. **Leia ao menos o capítulo
"No Silver Bullet".**

---

**6. Feathers, Michael. *Working Effectively with Legacy Code*. Prentice Hall,
2004. ISBN 978-0131177055.**

Origem do **teste de caracterização** — a técnica indispensável para migração
conduzida por agente ([exemplo 10](06-exemplos.md)). Define código legado como
"código sem testes", definição que ficou ainda mais pertinente.

**Nível:** intermediário. **Envelheceu?** Não. **Em português:**
*Trabalho Eficaz com Código Legado*, Bookman.

---

**7. Fowler, Martin. *Refactoring: Improving the Design of Existing Code*,
2ª edição. Addison-Wesley, 2018. ISBN 978-0134757599.**

Ficou mais relevante justamente porque a refatoração está desaparecendo dos
dados — de 21% de código movido em 2022 para 3,8% em 2026 (GitClear). Saber
refatorar é agora um diferencial escasso.

**Nível:** intermediário. **Em português:** *Refatoração*, Novatec (2ª ed.).

---

**8. Beck, Kent. *Test-Driven Development: By Example*. Addison-Wesley, 2002.
ISBN 978-0321146533.**

O método de escrever o critério antes da solução. É literalmente o passo 3 do
[04-como-comecar](04-como-comecar.md).

**Nível:** iniciante a intermediário. **Em português:**
*TDD: Desenvolvimento Guiado por Testes*, Bookman.

---

**9. Hunt, Andrew; Thomas, David. *The Pragmatic Programmer: Your Journey to
Mastery*, 20th Anniversary Edition. Addison-Wesley, 2019.
ISBN 978-0135957059.**

Ofício em estado bruto. Os capítulos sobre automação, ortogonalidade e "não
programe por coincidência" leem-se como escritos para 2026.

**Nível:** todos. **Em português:** *O Programador Pragmático*, Bookman
(edição de 20 anos).

---

**10. Forsgren, Nicole; Humble, Jez; Kim, Gene. *Accelerate: The Science of
Lean Software and DevOps*. IT Revolution, 2018. ISBN 978-1942788331.**

A base metodológica dos relatórios DORA que este curso cita. Ensina, além dos
achados, **como medir desempenho de engenharia sem se enganar** — que é
exatamente a competência que falta no debate sobre IA.

**Nível:** intermediário. **Em português:** *Accelerate*, Alta Books.

---

**11. Winters, Titus; Manshreck, Tom; Wright, Hyrum. *Software Engineering at
Google: Lessons Learned from Programming Over Time*. O'Reilly, 2020.
ISBN 978-1492082798.**

A tese — "engenharia de software é programação integrada ao tempo" — é o
antídoto direto contra otimizar a escrita ignorando a manutenção. Os capítulos
sobre revisão de código e automação em larga escala são diretamente aplicáveis.

**Nível:** intermediário a avançado.
**Legalmente gratuito:** sim, versão HTML completa em
https://abseil.io/resources/swe-book. **Em português:** Novatec.

---

**12. Farley, Dave. *Modern Software Engineering: Doing What Works to Build
Better Software Faster*. Addison-Wesley, 2021. ISBN 978-0137314911.**

Argumenta que engenharia de software é ciência aplicada: hipótese, experimento,
medição. É o enquadramento certo para decidir se a IA está ajudando **no seu
caso**.

**Nível:** intermediário. **Em português:** *Engenharia de Software Moderna*,
Alta Books.

---

## Parte III · Segurança e teoria

**13. Adkins, Heather et al. *Building Secure and Reliable Systems*. O'Reilly /
Google, 2020. ISBN 978-1492083122.**

Princípios de menor privilégio, defesa em profundidade e raio de explosão — a
base conceitual do isolamento de agentes ([22-seguranca](22-seguranca.md)).

**Legalmente gratuito:** sim, PDF oficial em https://sre.google/books/.

---

**14. Sipser, Michael. *Introduction to the Theory of Computation*, 3ª edição.
Cengage Learning, 2012. ISBN 978-1133187790.**

Para quem quiser o teorema de Rice com rigor, e não como slogan
([60-teoria-avancada](60-teoria-avancada.md)).

**Nível:** avançado. **Em português:** *Introdução à Teoria da Computação*,
Cengage.

---

**15. Huyen, Chip. *AI Engineering: Building Applications with Foundation
Models*. O'Reilly, 2025.**

**Atenção ao escopo:** é sobre construir produtos **com** modelos — RAG,
avaliação, otimização, implantação. **Não** é sobre usar IA para programar.
Está aqui porque a confusão entre os dois assuntos é constante e custa tempo de
muita gente. Se o seu objetivo é o cargo de *AI Engineer*, comece por aqui;
se é este curso, não é a sua leitura.

**Nível:** intermediário a avançado. Ver também
[agentes-de-ia](../agentes-de-ia/00-MAPA.md) e
[engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) desta pasta.

---

## Legalmente gratuitos

| Obra | Onde |
|---|---|
| *Software Engineering at Google* | https://abseil.io/resources/swe-book |
| *Building Secure and Reliable Systems* | https://sre.google/books/ |
| *Site Reliability Engineering* (Google) | https://sre.google/books/ |
| *Pro Git* (Chacon & Straub), **em português** | https://git-scm.com/book/pt-br/v2 |
| Relatórios DORA | https://dora.dev/research/ |
| *No Silver Bullet* (ensaio avulso) | amplamente disponível; verifique a licença da cópia |

---

## Roteiro de leitura sugerido

| Situação | Leia, nesta ordem |
|---|---|
| **Quero começar hoje** | Barbini (*Process Over Magic*) → este curso, [17](17-verificacao-e-testes.md) |
| **Quero entender a mudança de papel** | Osmani → Brooks (*No Silver Bullet*) |
| **Vou liderar a adoção no time** | Forsgren (*Accelerate*) → DORA 2025 → Kim & Yegge (com ceticismo) |
| **Tenho base legada para migrar** | Feathers → Fowler |
| **Quero a base de verificação** | Beck (TDD) → Winters (cap. de revisão) → Farley |
| **Segurança de agentes** | Adkins → [22-seguranca](22-seguranca.md) |
| **Quero a teoria** | Sipser (Rice) → [60-teoria-avancada](60-teoria-avancada.md) |

---

## O que **não** recomendo

Dito por economia do seu tempo:

- **Livros de "100 prompts para desenvolvedores".** O conteúdo envelhece em
  meses e a habilidade que ensina é a que menos importa ([75](75-armadilhas.md),
  mito 2).
- **Livros de 2023 sobre ChatGPT para programadores.** Anteriores aos agentes;
  descrevem um fluxo de trabalho que praticamente não existe mais.
- **Qualquer livro que prometa multiplicador.** "10× developer com IA" é
  marketing, e o [24](24-produtividade-o-que-diz-a-evidencia.md) mostra por quê.

---

## Nota de método

Todos os dados bibliográficos foram conferidos na web em 20/08/2026 (páginas de
editora, catálogos de livraria e registros de ISBN). Onde não encontrei
confirmação de um campo — número de páginas, edição em português, data exata —
**omiti o campo** em vez de estimar. Ausência aqui significa "não confirmei",
não "não existe".

---

## Autoteste

1. Qual é o único livro específico que você leria se só pudesse ler um, e por quê?
2. Por que o livro de Taulli (2024) envelheceu, e o que ainda se aproveita dele?
3. Onde eu discordo do livro de Kim e Yegge, e com que leitura você deve
   calibrá-lo?
4. Qual conceito de Feathers é indispensável para migração com agente?
5. Por que Fowler (*Refactoring*) ficou **mais** relevante, segundo os dados?
6. Qual é a tese de *Software Engineering at Google* e por que ela é o antídoto
   contra otimizar só a escrita?
7. Cite quatro obras legalmente gratuitas e onde encontrá-las.
8. Por que o livro de Chip Huyen está na lista se não é sobre este assunto?
9. Cite três tipos de livro que este arquivo desaconselha e o motivo.
10. O que significa a ausência de um campo (ex.: número de páginas) numa entrada
    desta bibliografia?

---

**Anterior:** [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md) ·
**Próximo:** [95-referencias](95-referencias.md)
