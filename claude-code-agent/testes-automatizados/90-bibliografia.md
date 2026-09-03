# 90 · Bibliografia comentada

`Nível: todos` · `Última atualização: 13/08/2026`

Livros com autor, título, editora e edição. Onde não tenho certeza da edição ou do ISBN,
**cito só autor e título** — nunca invento número.

Marcação usada:
🆓 legalmente gratuito · 🇧🇷 existe edição em português · ⭐ leitura essencial

---

## 1. Se você só puder ler três

| # | Livro | Por quê |
|---|---|---|
| 1 | **Khorikov — *Unit Testing: Principles, Practices, and Patterns*** | o modelo mental mais útil do campo: os quatro pilares e a tese de que eles são excludentes |
| 2 | **Feathers — *Working Effectively with Legacy Code*** | resolve o problema que você **vai** ter: código real sem testes |
| 3 | **Beck — *Test-Driven Development: By Example*** | curto, prático, e você entende TDD de verdade em uma tarde |

Nessa ordem. O primeiro dá o critério; o segundo dá a saída; o terceiro dá o ritmo.

---

## 2. Fundamentos e prática

### ⭐ Vladimir Khorikov — *Unit Testing: Principles, Practices, and Patterns*
Manning, 2020.
**Nível:** intermediário. **Envelheceu?** Não.

O livro que este curso mais usa. Introduz os **quatro pilares** (proteção contra regressão,
resistência a refatoração, retorno rápido, manutenibilidade) e defende que os três primeiros
são mutuamente excludentes — o que transforma "como testar" de questão de gosto em questão de
trade-off.

Também é o tratamento mais claro que existe da divisão clássica × mockista, com a distinção
prática entre dependências **dentro** e **fora** do processo. Os exemplos são em C#, e isso
importa pouco: as ideias são independentes de linguagem.

**Crítica honesta:** é opinativo, e às vezes apresenta preferência como consenso. Leia sabendo
disso.

---

### ⭐ Michael Feathers — *Working Effectively with Legacy Code*
Prentice Hall, 2004. 🇧🇷 *Trabalho eficaz com código legado* (Bookman)
**Nível:** intermediário–avançado. **Envelheceu?** Os exemplos em Java/C++ sim; as técnicas não.

A definição que ficou: **"código legado é código sem testes"**. O livro é um catálogo de
técnicas para introduzir testes em código que não foi feito para isso: **costuras** (*seams*),
testes de caracterização, quebra de dependência, e um capítulo por sintoma
("Não consigo rodar este método num arnês de teste", "Meu aplicativo é só chamadas de API").

**É o livro que resolve o problema real da maioria das pessoas.** A relevância dele em 2026 é
maior, não menor: agora há também código legado gerado por IA.

---

### ⭐ Kent Beck — *Test-Driven Development: By Example*
Addison-Wesley, 2002. 🇧🇷 *TDD: Desenvolvimento Guiado por Testes* (Bookman)
**Nível:** iniciante–intermediário. **Envelheceu?** Não. É curto e continua o melhor sobre o assunto.

Duas partes práticas — um exemplo de dinheiro multimoeda em Java e um framework xUnit em
Python, construídos passo a passo — e uma terceira de padrões. A construção do xUnit em Python
é a melhor forma de entender **como um corredor de testes funciona por dentro**.

**Onde ele decepciona:** não trata de código legado, de teste de integração ou de arquitetura.
É deliberadamente estreito.

---

### Gerard Meszaros — *xUnit Test Patterns: Refactoring Test Code*
Addison-Wesley, 2007.
**Nível:** avançado. **Envelheceu?** Parcialmente — a linguagem dos exemplos, não a taxonomia.

O catálogo de referência. É daqui que vêm **dummy, stub, spy, mock e fake**, além dos
antipadrões (*Assertion Roulette*, *Erratic Test*, *Fragile Test*, *Obscure Test*).

É um **livro de consulta de 900 páginas**, não de leitura linear. O site
[xunitpatterns.com](http://xunitpatterns.com/) traz boa parte do conteúdo — vale como
referência rápida.

---

### Steve Freeman & Nat Pryce — *Growing Object-Oriented Software, Guided by Tests*
Addison-Wesley, 2009.
**Nível:** avançado. **Envelheceu?** Java datado; método atual.

O manifesto da **escola de Londres**: TDD *outside-in*, com mocks como forma de descobrir as
interfaces das colaboradoras antes de elas existirem. Um dos autores é coautor do artigo que
inventou os mock objects.

**Leia junto com Khorikov**, que argumenta contra boa parte disso. As duas leituras juntas
valem mais que qualquer uma isolada — é o melhor jeito de formar opinião própria sobre a
disputa.

---

### Roy Osherove — *The Art of Unit Testing*
Manning. 3ª edição, 2021 (exemplos em JavaScript).
**Nível:** iniciante–intermediário.

Prático e acessível. A 3ª edição migrou de C# para JavaScript, o que o torna a porta de
entrada mais direta para quem vem do front-end. Cobre nomenclatura, dublês, testabilidade e
integração contínua sem se aprofundar em nenhum.

**Compare com Khorikov:** Osherove é mais introdutório e menos rigoroso nos trade-offs.

---

### Lisa Crispin & Janet Gregory — *Agile Testing* e *More Agile Testing*
Addison-Wesley, 2009 e 2014.
**Nível:** intermediário. Foco em **processo e time**, não em código.

Os "quadrantes de teste ágil" e a discussão sobre o papel do QA num time que entrega
continuamente. Útil se você lidera, ou se precisa convencer um time. Pouco útil se você quer
escrever código de teste.

---

## 3. Clássicos que continuam valendo

### Glenford Myers — *The Art of Software Testing*
Wiley. 1ª edição 1979; 3ª edição 2011 (com Badgett e Sandler).
**Nível:** intermediário. **Envelheceu?** O contexto sim; os fundamentos não.

De onde vem a definição *"testar é executar um programa com a intenção de encontrar
defeitos"*. As técnicas de projeto de caso de teste — partição de equivalência, valor de
fronteira, tabela de decisão, cobertura de condição — estão aqui, e continuam sendo a base do
que se ensina hoje. O exercício de abertura ("escreva casos de teste para um programa que diz
se três números formam um triângulo") continua humilhando gente experiente.

Ignore as partes sobre inspeção de código em papel e sobre mainframe.

---

### Boris Beizer — *Software Testing Techniques*
Van Nostrand Reinhold, 2ª edição 1990.
**Nível:** avançado. **Envelheceu?** Muito no contexto; pouco na teoria.

Tratamento formal de teste de fluxo de controle, fluxo de dados, teste de domínio e teste
sintático. Denso e datado, mas é a referência quando você precisa da teoria por trás dos
critérios de cobertura.

---

### Cem Kaner, James Bach & Bret Pettichord — *Lessons Learned in Software Testing*
Wiley, 2002.
**Nível:** intermediário. 293 lições curtas.

A voz da escola **context-driven**, que é o contraponto saudável ao excesso de processo. Muita
franqueza sobre política organizacional, métricas enganosas e limites do que teste consegue
entregar. Envelheceu bem porque não fala de ferramenta.

---

### Frederick Brooks — *The Mythical Man-Month*
Addison-Wesley, 1975; edição de aniversário 1995. 🇧🇷 *O Mítico Homem-Mês* (Alta Books)
**Nível:** todos.

Não é livro de testes, mas o ensaio *No Silver Bullet* é a vacina contra qualquer promessa de
solução mágica — inclusive as de 2026 sobre IA. Leitura de uma hora com retorno de uma
carreira.

---

## 4. Projeto e arquitetura (onde a testabilidade nasce)

### Martin Fowler — *Refactoring: Improving the Design of Existing Code*
Addison-Wesley. 2ª edição 2018 (exemplos em JavaScript). 🇧🇷 *Refatoração* (Novatec)
**Nível:** intermediário. ⭐ para quem já testa.

O primeiro capítulo enuncia a relação: **refatorar exige testes**; sem eles, você está
reescrevendo às cegas. O catálogo de refatorações é o vocabulário que falta para descrever o
que fazer com o código que o teste denunciou.

A 2ª edição em JavaScript é mais acessível que a 1ª em Java.

---

### Robert C. Martin — *Clean Code* / *Clean Architecture*
Prentice Hall, 2008 / 2017. 🇧🇷 *Código Limpo* / *Arquitetura Limpa* (Alta Books)
**Nível:** iniciante–intermediário.

**Recomendação com ressalva explícita.** Os capítulos sobre testes (as regras F.I.R.S.T.,
"testes são cidadãos de primeira classe") são bons e amplamente citados. Boa parte do resto é
opinião apresentada como princípio, e há crítica técnica substantiva a vários dos conselhos
(funções minúsculas em excesso, comentários como falha).

Leia sabendo que é opinião forte, não consenso. E leia Fowler junto.

---

### Eric Evans — *Domain-Driven Design*
Addison-Wesley, 2003. 🇧🇷 *Domain-Driven Design* (Alta Books)
**Nível:** avançado.

Conexão com testes: o **domínio isolado** que o DDD propõe é exatamente o núcleo puro que se
testa com `assert` e sem dublê. Livro denso; para uma versão curta, o *Domain-Driven Design
Distilled* (Vaughn Vernon, 2016) cobre as ideias centrais em ~150 páginas.

---

## 5. Legalmente gratuitos 🆓

| Obra | Autor | Onde | Observação |
|---|---|---|---|
| 🆓 **Software Engineering at Google** | Winters, Manshreck & Wright (O'Reilly, 2020) | [abseil.io/resources/swe-book](https://abseil.io/resources/swe-book) | **Leia os capítulos 11 a 14.** É o melhor relato público de teste em escala real: o que a Google mediu sobre testes pequenos/médios/grandes, instabilidade, e por que eles proíbem certas práticas. Gratuito em HTML por decisão dos autores. |
| 🆓 **The Architecture of Open Source Applications** | vários | [aosabook.org](https://aosabook.org/) | volumes com capítulos sobre design testável de projetos reais |
| 🆓 **Pro Git** | Chacon & Straub | [git-scm.com/book/pt-br/v2](https://git-scm.com/book/pt-br/v2) | 🇧🇷 pré-requisito para CI; tradução oficial boa |
| 🆓 **Python — documentação oficial** | PSF | [docs.python.org/pt-br/3](https://docs.python.org/pt-br/3/) | 🇧🇷 seções `unittest`, `doctest`, `unittest.mock` |
| 🆓 **xUnit Patterns (site)** | Meszaros | [xunitpatterns.com](http://xunitpatterns.com/) | boa parte do conteúdo do livro |
| 🆓 **martinfowler.com** | Fowler | [martinfowler.com/testing](https://martinfowler.com/testing/) | os artigos conceituais de referência, todos abertos |
| 🆓 **Google Testing Blog** | Google | [testing.googleblog.com](https://testing.googleblog.com/) | arquivo de ~20 anos |
| 🆓 **ISTQB Syllabus e Glossário** | ISTQB | [istqb.org](https://www.istqb.org/) | material oficial da certificação, gratuito |

---

## 6. Sobre traduções para o português

| Livro | Tradução | Avaliação honesta |
|---|---|---|
| *Código Limpo* (Alta Books) | existe | tradução aceitável; termos técnicos às vezes traduzidos onde não deveriam |
| *Refatoração* (Novatec) | existe | boa |
| *TDD: Desenvolvimento Guiado por Testes* (Bookman) | existe | aceitável |
| *Trabalho eficaz com código legado* (Bookman) | existe | aceitável |
| *O Mítico Homem-Mês* (Alta Books) | existe | boa |
| **Khorikov, Meszaros, Freeman & Pryce, Myers, Beizer** | **não localizei edição em português** | leia em inglês |

> **Sobre disponibilidade:** editoras técnicas brasileiras tiram títulos de catálogo com
> frequência, e edições esgotam. Confirme antes de comprar; usados costumam ser a saída para
> os mais antigos.
>
> Não listo ISBN aqui por opção deliberada: números de ISBN variam por edição, tiragem e
> encadernação, e um ISBN errado é pior que nenhum.

---

## 7. Roteiro de leitura por objetivo

| Você quer... | Leia, nesta ordem |
|---|---|
| **começar do zero** | este material → Beck (*TDD by Example*) → Osherove |
| **melhorar a suíte que já tem** | Khorikov → Meszaros (consulta) → cap. 11–14 do *SWE at Google* |
| **domar código legado** | Feathers → Fowler (*Refactoring*) → Khorikov |
| **liderar um time** | *SWE at Google* (11–14) → Crispin & Gregory → Kaner et al. |
| **entender a teoria** | Myers → Beizer → os artigos de [95-referencias.md](95-referencias.md) |
| **testar front-end** | documentação da Testing Library → Osherove (3ª ed.) |
| **gastar R$ 0** | *SWE at Google* + martinfowler.com + Google Testing Blog + xunitpatterns.com |

---

## Autoteste

1. Quais são os três livros essenciais e o que cada um resolve?
2. Qual é a definição de código legado de Feathers, e por que ela é útil?
3. Por que ler Khorikov **e** Freeman & Pryce juntos?
4. O que Meszaros contribuiu que se usa todo dia sem citar a fonte?
5. Qual livro contém a definição de teste mais citada do campo, e de que ano é?
6. Qual é a melhor obra gratuita sobre teste em escala, e quais capítulos ler?
7. Por que *Clean Code* aparece com ressalva?
8. Qual livro de 1975 continua sendo vacina contra promessa mágica, e qual ensaio dele?
9. Cite três obras legalmente gratuitas e onde encontrá-las.
10. Você lidera um time e quer melhorar a qualidade. O que lê, nesta ordem?
