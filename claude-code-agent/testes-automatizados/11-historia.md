# 11 · História — como chegamos aqui

`Nível: intermediário` · `Última atualização: 12/08/2026`

História importa aqui por um motivo prático: quase toda "boa prática" de teste que você vai
encontrar é a resposta a um problema concreto de uma época. Sabendo qual era o problema,
você sabe **quando a prática ainda se aplica** e quando virou culto de carga.

---

## Linha do tempo

```
1947  ┃ a mariposa no Mark II — a etimologia (falsa) de "bug"
1949  ┃ Turing: "Checking a Large Routine" — a primeira ideia de asserção
1968  ┃ conferência da OTAN em Garmisch: nasce o termo "engenharia de software"
1970  ┃ Dijkstra: "testes mostram a presença de defeitos, nunca a ausência"
1972  ┃ primeira conferência dedicada a teste de software (Chapel Hill)
1975  ┃ Goodenough & Gerhart: primeira teoria formal de adequação de teste
1978  ┃ DeMillo, Lipton & Sayward: análise de mutação
1979  ┃ Myers: "The Art of Software Testing" — o primeiro livro de referência
1981  ┃ Boehm: "Software Engineering Economics" — a curva de custo do defeito
1982  ┃ Weyuker: o problema do oráculo ("programas não-testáveis")
1986  ┃ modelo V: teste como espelho das fases de desenvolvimento
      ┃
1994  ┃ Kent Beck escreve o SUnit, para Smalltalk ★
1997  ┃ Beck e Erich Gamma escrevem o JUnit num voo Zurique→Atlanta ★
1999  ┃ Beck: "Extreme Programming Explained" — teste vira prática diária
2000  ┃ Mackinnon, Freeman & Craig: "Endo-Testing" — nascem os mock objects
2000  ┃ Claessen & Hughes: QuickCheck — teste baseado em propriedades
2001  ┃ Python 2.1 ganha o módulo `unittest` (porte do PyUnit, que é porte do JUnit)
2001  ┃ CruiseControl: primeiro servidor de integração contínua popular
2002  ┃ Beck: "Test-Driven Development: By Example"
2003  ┃ Dan North: BDD — "given/when/then" no lugar de "test"
2004  ┃ Selenium (Jason Huggins, ThoughtWorks)
2004  ┃ Holger Krekel cria o `py.test`, dentro do projeto PyPy ★
2004  ┃ Feathers: "Working Effectively with Legacy Code"
2005  ┃ Hudson (que vira Jenkins em 2011)
2007  ┃ Meszaros: "xUnit Test Patterns" — a taxonomia dos dublês
2007  ┃ Fowler: "Mocks Aren't Stubs" — a disputa clássica × mockista, nomeada
2007  ┃ Simon Stewart: WebDriver
2009  ┃ Mike Cohn: a **pirâmide de testes**, em "Succeeding with Agile"
2009  ┃ Freeman & Pryce: "Growing Object-Oriented Software, Guided by Tests"
      ┃
2010  ┃ pytest 2.0, independente do `py` ★
2010  ┃ Jasmine (JavaScript); 2011: Mocha
2011  ┃ Travis CI — CI como serviço, grátis para código aberto
2013  ┃ Hypothesis (David MacIver) traz QuickCheck para Python
2014  ┃ Jest (Facebook)
2014  ┃ Docker populariza ambiente de teste descartável
2016  ┃ Testing Library (Kent C. Dodds) — "teste como o usuário usa"
2017  ┃ Cypress
2018  ┃ WebDriver vira Recomendação do W3C
2018  ┃ Kent C. Dodds: o "Testing Trophy", crítica à pirâmide
2019  ┃ GitHub Actions — CI dentro do repositório
2020  ┃ Playwright (Microsoft)
2020  ┃ Khorikov: "Unit Testing" — os quatro pilares
2021  ┃ Vitest (Anthony Fu) — corredor sobre o Vite
2023  ┃ Node 20: `node:test` estável — corredor embutido no runtime
2024+ ┃ geração de teste por LLM sai do laboratório e entra nas IDEs
2026  ┃ pytest 9 · Vitest 4 · Jest 30 · Node 24/26 com `node:test` maduro
```

★ = marcos diretamente ligados às ferramentas que este curso usa.

---

## 1. Antes de existir "teste": 1947–1970

### A mariposa que não explica nada

Em 9 de setembro de 1947, a equipe de Grace Hopper encontrou uma mariposa presa num relé do
Harvard Mark II, colou-a no caderno de bordo e escreveu *"First actual case of bug being
found"*. A anedota é verdadeira e é frequentemente citada como a origem da palavra "bug".

**Não é.** A palavra já era usada por engenheiros no século XIX — há registro em carta de
Thomas Edison, de 1878, falando de "bugs" em invenções. O que a anedota mostra é justamente
o contrário: a piada só funciona porque a palavra **já** existia. Vale conhecer o episódio
para não repetir a versão errada.

### Turing, 1949: a primeira asserção

No artigo *Checking a Large Routine*, apresentado em Cambridge em junho de 1949, Alan Turing
propôs anexar a cada ponto do programa uma **afirmação verificável** sobre o estado da
máquina, de modo que a correção do todo pudesse ser argumentada. É a semente conceitual de
duas coisas: da asserção que você escreve hoje, e da verificação formal.

### Dijkstra, 1970: o limite

> *"Program testing can be used to show the presence of bugs, but never to show their
> absence."*

Dijkstra dizia isso para argumentar a favor de provas de correção, não contra testes. A
frase, porém, sobreviveu ao argumento e virou o enunciado do limite fundamental do campo:
**testar é amostrar**. Tudo o que veio depois é engenharia de amostragem.

---

## 2. A era da fase de teste: 1970–1995

Neste período, o modelo dominante era o **cascata**, e o teste era uma **fase**: projeta,
codifica, testa, entrega. Duas consequências moldaram tudo:

1. **Equipes separadas.** Quem programava não testava. Existia o "departamento de QA", às
   vezes noutro prédio, às vezes noutro país.
2. **Ciclo longo.** Um defeito introduzido em março era encontrado em outubro.

O segundo ponto gerou o gráfico mais citado — e mais mal citado — do campo: a **curva de
custo de Boehm** (*Software Engineering Economics*, 1981), segundo a qual corrigir um
defeito em produção custa ordens de grandeza mais que corrigi-lo no projeto.

**Honestidade sobre esse número:** os dados originais de Boehm vêm de projetos aeroespaciais
dos anos 1970, com ciclos de anos. Os multiplicadores frequentemente citados ("100×") foram
extrapolados muito além do que os dados sustentam, e pesquisadores contestam a magnitude há
duas décadas. **Que corrigir tarde custa mais, ninguém contesta** — e a razão é intuitiva:
o contexto se perde e outras coisas foram construídas em cima. Mas se alguém apresentar
"100×" como fato medido, desconfie.

**O que essa era nos deixou de bom:** as técnicas de projeto de caso de teste — partição de
equivalência, análise de valor de fronteira, tabela de decisão, teste de transição de
estado. Todas continuam valendo, e estão em [10-fundamentos.md](10-fundamentos.md) e
[70-pratica.md](70-pratica.md). São a herança do rigor daquele período.

**O que ela nos deixou de ruim:** a ideia de que teste é atividade de outra pessoa, depois;
e a papelada (planos de teste de 200 páginas descrevendo o que seriam 40 linhas de código).

---

## 3. A virada: 1994–2002

### SUnit e JUnit

Em 1994, **Kent Beck** escreveu o **SUnit** para Smalltalk. Era pequeno — poucas classes —
e estabeleceu o padrão que sobreviveu 30 anos: *test case*, *test suite*, *fixture*,
`setUp`, `tearDown`, asserções.

Em 1997, num voo de Zurique para Atlanta rumo à OOPSLA, **Erich Gamma** pediu a Beck que lhe
ensinasse Java. O que os dois escreveram no voo virou o **JUnit**. Daí nasceu a família
**xUnit**: NUnit, PyUnit, CppUnit, PHPUnit e dezenas de outras — todas com a mesma anatomia.

**Por que isso foi uma revolução, e não só uma biblioteca:** antes do xUnit, escrever um
teste significava escrever um `main()` que imprimia coisas e você lia. O xUnit fez três
coisas juntas: **descoberta automática** dos testes, **isolamento** entre eles, e um
**veredito binário**. Foi isso que tornou possível rodar mil testes num comando.

### Extreme Programming: o teste vira rotina

Beck publicou *Extreme Programming Explained* em 1999. XP trouxe várias práticas; duas
mudaram este campo para sempre:

- **teste automatizado escrito por quem programa**, junto com o código;
- **integração contínua**: integrar e rodar tudo várias vezes ao dia.

Em 2002, Beck publicou *Test-Driven Development: By Example*, formalizando o ciclo
**vermelho → verde → refatorar**. Ver [15-tdd.md](15-tdd.md).

### Mocks nascem — e a divisão começa

No ano 2000, num artigo apresentado na conferência XP, Tim Mackinnon, Steve Freeman e Philip
Craig descreveram o **mock object**: um objeto falso que **verifica como foi usado**. O
artigo se chamava *Endo-Testing: Unit Testing with Mock Objects*.

A ideia nasceu de um problema real: como testar um objeto que só existe para conversar com
outros? Mas ela abriu uma divisão que nunca fechou. A "escola de Londres", em torno dos
autores, passou a isolar cada classe de todas as suas colaboradoras. A "escola clássica",
em torno de Beck, continuou testando comportamentos com objetos reais.

Martin Fowler nomeou a disputa em *Mocks Aren't Stubs* (2007). Ela está viva em 2026 e é o
assunto de [13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md).

---

## 4. Python: do `unittest` ao pytest

O **`unittest`** entrou na biblioteca padrão do Python em 2001 (Python 2.1). Ele é um porte
do **PyUnit**, de Steve Purcell, que por sua vez é um porte do JUnit. Isso explica seu
aspecto: classes obrigatórias, `self.assertEqual`, `camelCase` — tudo herança de Java, num
idioma que não é o de Python.

O **py.test** começou em 2004, dentro do PyPy. Holger Krekel vinha refatorando o arcabouço
de teste do PyPy desde 2003 e queria escrever asserções com o `assert` da própria linguagem,
em vez de decorar dezenas de métodos `assertXxx`. Batizou o pacote de `std`, depois `py`, e
`std.utest` virou `py.test`.

Em novembro de 2010 saiu o **pytest 2.0**, já independente. O nome do comando continuou
sendo `py.test` até 2016, quando o pytest 3.0 passou a recomendar `pytest`.

**Por que o pytest venceu.** Três decisões, em ordem de importância:

1. **Reescrita de asserção** (*assertion rewriting*). O pytest manipula o bytecode dos
   arquivos de teste para que um `assert a == b` que falha mostre os valores de `a` e `b`.
   Isso eliminou a necessidade da API `assertEqual`/`assertIn`/`assertAlmostEqual` inteira.
2. **Fixtures por injeção.** Em vez de `setUp` herdado, você pede o que precisa pelo nome do
   parâmetro. Fixtures compõem, têm escopo, e só rodam para quem as pede.
3. **Compatibilidade.** O pytest roda testes `unittest` sem alteração. Migrar era gratuito —
   e essa foi provavelmente a decisão estratégica mais importante das três.

**Estado em 2026:** o pytest 9 (novembro de 2025) removeu o que restava do estilo `nose`,
o namespace legado `pytest.collect` e os testes baseados em `yield`. Se você encontrar
tutorial usando qualquer um deles, é anterior a 2015.

---

## 5. JavaScript: a era das três bibliotecas, e o fim dela

O JavaScript demorou mais a se organizar, e o motivo é ambiental: por muito tempo o código
rodava em **navegadores diferentes com comportamentos diferentes**, e não havia runtime de
linha de comando padrão. O Node.js só apareceu em 2009.

A geração de 2010–2015 montava a suíte com **três pacotes**:

| Papel | Pacote típico |
|---|---|
| corredor | Mocha |
| asserções | Chai (`expect(x).to.equal(y)`) |
| dublês | Sinon |
| cobertura | Istanbul |
| navegador | Karma + PhantomJS |

Funcionava, mas cada projeto montava um Frankenstein diferente, e configurar levava um dia.

**Jest** (Facebook, 2014) atacou exatamente isso: um pacote com corredor, asserções, mocks,
cobertura e snapshots, com configuração quase zero. Venceu por conveniência — e a onda do
React ajudou muito.

**Vitest** (2021, Anthony Fu) atacou o problema seguinte: o Jest nasceu no mundo CommonJS e
precisava do Babel para lidar com módulos ES e TypeScript, o que ficou lento e cheio de
armadilhas. O Vitest reaproveita o pipeline do **Vite** — ESM e TypeScript nativos, sem
etapa de compilação separada — mantendo a API do Jest quase idêntica, para a migração ser
barata. É a mesma jogada estratégica do pytest com o `unittest`.

**`node:test`** (estável no Node 20, 2023) fecha o ciclo: o corredor de testes virou parte
do runtime, como já era em Go e em Rust. Zero dependência, zero configuração, zero
`node_modules`. Em 2026 ele já tem mocks, temporizadores falsos, cobertura, *watch* e
snapshots.

**Opinião profissional, declarada como opinião:** a direção é clara — corredor embutido no
runtime para bibliotecas e serviços; Vitest quando há front-end, DOM e uma cadeia de
compilação já montada; Jest quando há legado que custa mais migrar do que manter. A era de
montar três pacotes acabou, e não volta.

---

## 6. A pirâmide, e a reação contra ela

**Mike Cohn** publicou a pirâmide de testes em *Succeeding with Agile* (2009): muitos
unitários na base, alguns de serviço no meio, poucos de interface no topo.

O contexto importa: em 2009, o topo eram testes de Selenium controlando o Internet Explorer,
que eram absurdamente lentos e frágeis. A pirâmide era um **remédio para o antipadrão do
sorvete de casquinha** (*ice-cream cone*): times que só tinham teste de interface, gastavam
horas por execução e viviam com a suíte vermelha.

**As críticas legítimas, a partir de ~2015:**

- as camadas mudaram de preço: o Playwright rodando *headless* em 2026 não é o Selenium com
  IE em 2009;
- "unitário" na base incentiva testar classe por classe, o que produz suítes acopladas à
  estrutura;
- a pirâmide não diz nada sobre **risco**, que é o critério que deveria governar.

**Kent C. Dodds** propôs em 2018 o **Testing Trophy**, com o peso maior nos testes de
**integração**, argumentando que é onde está a melhor relação entre confiança e custo em
aplicações de front-end modernas.

Ambos os modelos são simplificações úteis, e nenhum é uma lei. O tratamento honesto dos dois
está em [12-tipos-e-piramide.md](12-tipos-e-piramide.md).

---

## 7. Integração contínua: de CruiseControl a GitHub Actions

O termo **integração contínua** aparece em Grady Booch (1991) e vira prática nomeada no XP.
A cadeia de ferramentas:

| Ano | Ferramenta | O que mudou |
|---|---|---|
| 2001 | CruiseControl | primeiro servidor de CI popular; você mantinha o servidor |
| 2005 | Hudson (→ Jenkins, 2011) | plugins para tudo; virou o padrão corporativo |
| 2011 | Travis CI | **CI como serviço**, grátis para código aberto — mudou tudo |
| 2015 | GitLab CI | pipeline como arquivo **dentro do repositório** |
| 2019 | GitHub Actions | idem, no maior hospedeiro de código do mundo |

A mudança conceitual foi de "servidor que alguém administra" para "arquivo YAML versionado
junto com o código". Isso fez a configuração de CI virar parte da revisão de código — e é
por isso que hoje se espera que qualquer projeto sério tenha CI desde o primeiro dia. Ver
[21-ci-e-automacao.md](21-ci-e-automacao.md).

---

## 8. As linhas de pesquisa, e onde elas encostam na prática

Nem tudo o que a academia produziu virou prática, mas quatro coisas viraram:

| Ideia | Origem | Onde você a encontra hoje |
|---|---|---|
| **análise de mutação** | DeMillo, Lipton & Sayward, 1978 | Stryker (JS), mutmut e Cosmic Ray (Python) |
| **teste por propriedades** | Claessen & Hughes (QuickCheck), 2000 | Hypothesis, fast-check, proptest |
| **fuzzing** | Miller et al., 1990 | OSS-Fuzz, `libFuzzer`, `atheris` |
| **teste metamórfico** | T. Y. Chen, 1998 | testes de sistemas de IA e de compiladores |

Repare no intervalo: mutação levou ~40 anos entre o artigo e o uso corriqueiro em CI. Isso é
normal no campo, e é um bom lembrete de que "estado da arte" e "prática comum" são coisas
diferentes. Detalhes em [60-teoria-avancada.md](60-teoria-avancada.md).

---

## 9. O que a história ensina

1. **Toda prática responde a um problema de uma época.** A pirâmide responde ao Selenium
   lento de 2009. Se seu contexto mudou, a prática pode ter de mudar.
2. **A conveniência vence a pureza.** pytest venceu por rodar testes `unittest`. Vitest
   venceu por copiar a API do Jest. Jest venceu por ser um pacote só. Nenhum venceu por ser
   teoricamente superior.
3. **A direção é sempre a mesma: encurtar o laço.** De "fase de teste em outubro" para
   "vermelho no editor em 200 ms". Tudo o que encurtou o laço pegou; tudo o que o alongou
   morreu.
4. **Números citados sem fonte envelhecem mal.** A curva de Boehm virou "100×" e o "100×"
   virou fato que não é. Desconfie de multiplicadores redondos.
5. **As disputas velhas continuam vivas** porque são trade-offs reais, não erros de um dos
   lados. Clássica × mockista tem 26 anos e não vai ser resolvida — o que se pode fazer é
   entender o que cada lado otimiza.

---

## Autoteste

1. A mariposa de 1947 é a origem da palavra "bug"? Justifique.
2. O que Turing propôs em 1949 e com o que isso se parece hoje?
3. Qual era o argumento de Dijkstra ao dizer que testes não mostram a ausência de defeitos?
4. O que a "era da fase de teste" nos deixou de bom, e de ruim?
5. Por que a curva de custo de Boehm deve ser citada com cuidado?
6. Quais três coisas o xUnit fez que não existiam antes dele?
7. Cite as três decisões que fizeram o pytest vencer o `unittest`, em ordem de importância.
8. Que problema o Jest resolveu em 2014? E o Vitest, em 2021?
9. Qual era o contexto de 2009 que explica a forma da pirâmide de testes?
10. Qual foi a mudança conceitual de Jenkins para GitHub Actions?
11. Quantos anos separam o artigo sobre análise de mutação do seu uso corriqueiro? O que isso ensina?
12. Qual é a "direção constante" que a história do campo mostra?

---

## Fontes consultadas (12/08/2026)

- [XUnit — Wikipedia](https://en.wikipedia.org/wiki/XUnit) · [JUnit — Wikipedia](https://en.wikipedia.org/wiki/JUnit) · [Kent Beck — Wikipedia](https://en.wikipedia.org/wiki/Kent_Beck)
- [History — documentação do pytest](https://docs.pytest.org/en/stable/history.html)
- [Digging into pytest's history — discussão nº 8667 no repositório do pytest](https://github.com/pytest-dev/pytest/discussions/8667)
- [Pytest — Wikipedia](https://en.wikipedia.org/wiki/Pytest)
- [Martin Fowler — Xunit](https://martinfowler.com/bliki/Xunit.html)
- Livros e artigos citados estão detalhados em [90-bibliografia.md](90-bibliografia.md) e
  [95-referencias.md](95-referencias.md).
