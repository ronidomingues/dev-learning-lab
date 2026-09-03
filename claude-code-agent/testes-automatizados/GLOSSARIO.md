# Glossário

`Última atualização: 13/08/2026`

Todo termo técnico usado no material, com o original em inglês. Ordem alfabética pelo termo
em português (ou pelo termo em inglês, quando é assim que o campo o usa).

---

## A

**AAA · Arrange–Act–Assert** — a estrutura de todo teste: preparar o cenário, executar a ação,
verificar o resultado. Ver [10](10-fundamentos.md) §3.

**Adequação de critério** (*test adequacy criterion*) — regra que diz quando um conjunto de
testes é "suficiente" (ex.: cobrir todos os ramos). Nenhum critério computável garante
correção. Ver [60](60-teoria-avancada.md) §3.

**AGPL** — licença copyleft que estende as obrigações da GPL ao software oferecido em rede.
Nenhuma ferramenta central deste curso a usa.

**Análise de mutação** (*mutation testing*) — injetar defeitos artificiais no código e medir
quantos a suíte detecta. Mede a **qualidade da suíte**. Ver [19](19-cobertura-e-metricas.md) §4.

**Análise estática** — verificar o código sem executá-lo (tipos, lint). A camada mais barata
da carteira de qualidade.

**Antipadrão** (*anti-pattern*) — solução comum que parece boa e produz dano. Ver
[75](75-armadilhas.md).

**Arnês de teste** (*test harness*) — a infraestrutura que roda os testes e coleta resultados.
Na prática, o corredor mais os utilitários do projeto.

**Asserção** (*assertion*) — a afirmação verificada pelo teste. Se falsa, o teste falha.

**Assertion rewriting** — mecanismo do pytest que reescreve o bytecode dos módulos de teste
para que um `assert` que falha mostre os valores intermediários. Ver [16](16-python-pytest.md) §3.

**Assertion roulette** — antipadrão: muitas asserções não relacionadas num teste só; a
primeira que falha esconde as demais.

**Autouse** — fixture do pytest que se aplica sem ser pedida. Poderosa e perigosa.

---

## B

**BDD** (*Behavior-Driven Development*) — variação de TDD com vocabulário
"dado/quando/então" (*given/when/then*), voltado a aproximar teste e regra de negócio.

**Borda** (*shell*, *edge*) — a camada do sistema que fala com o mundo (I/O). Deve ser fina e
sem regra. Ver [20](20-testabilidade-e-design.md) §3.

**Branch coverage** — ver *cobertura de ramo*.

---

## C

**Caixa-branca / caixa-preta** (*white-box / black-box*) — teste com ou sem conhecimento da
implementação interna.

**Caminho feliz** (*happy path*) — o fluxo em que tudo dá certo. O caminho triste é o resto,
e vale metade da suíte.

**CI** (*Continuous Integration*, integração contínua) — integrar o trabalho no tronco com
frequência, com verificação automática a cada integração. Ver [21](21-ci-e-automacao.md).

**Cobertura** (*code coverage*) — fração do código **executada** pelos testes. Não mede
verificação. Ver [19](19-cobertura-e-metricas.md).

**Cobertura de caminho** (*path coverage*) — todos os caminhos pelo grafo de fluxo. Cresce
exponencialmente; inviável.

**Cobertura de condição** — cada condição atômica de uma decisão assume verdadeiro e falso.

**Cobertura de linha** (*statement coverage*) — o critério mais fraco. Insuficiente sozinho.

**Cobertura de ramo** (*branch coverage*) — cada decisão tomada nos dois sentidos. **O padrão
que se deve ligar.**

**Composition root** — o único lugar, na borda, onde o grafo de objetos é montado.

**conftest.py** — arquivo do pytest descoberto automaticamente, que expõe fixtures e ganchos
para o diretório e subdiretórios.

**Corredor** (*test runner*) — o programa que descobre, executa e relata os testes: pytest,
`node:test`, Vitest, Jest.

**Costura** (*seam*) — ponto onde se pode alterar o comportamento **sem editar naquele
ponto**. Termo de Michael Feathers. Ver [20](20-testabilidade-e-design.md) §5.

---

## D

**Defeito** (*fault*, *bug*) — o trecho de código incorreto. Distinto de **erro** e de
**falha**. Ver [10](10-fundamentos.md) §2.

**Determinismo** — mesma entrada, mesmo resultado, sempre. Requisito de todo teste.

**Diff coverage** — cobertura calculada só sobre as linhas que o PR mudou. Mais acionável que
a cobertura global.

**Doctest** — testes escritos dentro do *docstring*, executáveis. Ver [16](16-python-pytest.md) §12.

**Dublê de teste** (*test double*) — objeto falso que substitui uma dependência real.
Guarda-chuva para dummy, stub, spy, mock e fake. Ver [14](14-dubles-de-teste.md).

**Dummy** — dublê que nunca é usado; existe só para preencher um argumento.

---

## E

**E2E** (*end-to-end*, ponta a ponta) — teste que exercita o sistema inteiro como um usuário.

**Efeito de acoplamento** (*coupling effect*) — hipótese de que uma suíte que detecta defeitos
simples também detecta a maioria dos complexos. Base da análise de mutação.

**Encolhimento** (*shrinking*) — reduzir um contraexemplo ao menor caso que ainda falha.
Central em teste por propriedades.

**Erro** (*error*, *mistake*) — o engano humano que produz o defeito.

**ESM** (*ECMAScript Modules*) — o sistema de módulos padrão do JavaScript (`import`/`export`),
por oposição ao CommonJS (`require`).

**Escopo** (*scope*) — em pytest, quantas vezes uma fixture é criada: `function`, `class`,
`module`, `package`, `session`.

---

## F

**Fake** — dublê com implementação funcional simplificada (repositório em memória, SQLite no
lugar de Postgres). O melhor dublê para dependências com estado.

**Falha** (*failure*) — o comportamento observável errado, em tempo de execução.

**Falso negativo** — teste passa, mas o código está errado. Teste inútil.

**Falso positivo** — teste falha, mas o código está certo. Teste ruim.

**FIRST** — mnemônico para propriedades de bom teste unitário: *Fast, Independent,
Repeatable, Self-validating, Timely*.

**Fixture** — o cenário preparado antes do teste; em pytest, também o mecanismo (função
provedora resolvida por nome de parâmetro).

**Flaky** (teste instável) — teste que passa e falha sem que nada mude. **Pior que não ter
teste**, porque treina o time a ignorar o vermelho.

**Functional core, imperative shell** — arquitetura com núcleo puro (regras, sem I/O) e casca
imperativa (I/O, sem regras).

**Fuzzing** — alimentar o programa com entradas geradas em massa para achar travamentos e
falhas de robustez.

---

## G

**Gancho** (*hook*) — ponto de extensão do corredor (`pytest_collection_modifyitems`), ou do
Git (`pre-commit`).

**Given/When/Then** — vocabulário BDD, equivalente a Arrange–Act–Assert.

---

## H

**Hipótese do programador competente** — hipótese de que os defeitos reais são pequenos
desvios de um programa quase correto. Sustenta a análise de mutação.

**Hoisting** (içamento) — mover uma declaração para o topo do escopo. `vi.mock`/`jest.mock`
são içados para antes dos `import`, o que causa surpresas. Ver [17](17-javascript-vitest-jest.md) §3.3.

---

## I

**Injeção de dependência** (*dependency injection*, DI) — passar as dependências de fora, em
vez de construí-las por dentro. Não exige framework: é passar parâmetro.

**Integração (teste de)** — teste que exercita a conversa entre duas ou mais peças, e/ou uma
dependência externa real.

**Invariante** — propriedade que deve valer sempre, independentemente da sequência de
operações.

**Isolamento** — (a) não tocar I/O; (b) não depender de outros testes. Os dois são
inegociáveis.

---

## L

**Legado (código)** — na definição de Michael Feathers: **código sem testes**. Não é
sinônimo de código velho.

---

## M

**MC-DC** (*Modified Condition/Decision Coverage*) — critério em que cada condição precisa
demonstrar isoladamente que afeta o resultado. Exigido pela DO-178C nível A.

**Metamórfico (teste)** — verifica **relações entre execuções** quando a saída correta é
desconhecida. Ver [60](60-teoria-avancada.md) §2.3.

**Mock** — dublê que verifica a **interação**: quais chamadas foram feitas, com quais
argumentos. Use com parcimônia, e só em fronteira externa.

**Monkeypatch** — substituir um atributo em tempo de execução. Em pytest, uma fixture nativa
que desfaz a alteração automaticamente.

**Mutante equivalente** — mutante sintaticamente diferente e semanticamente idêntico ao
original; impossível de matar, e indecidível de detectar.

---

## N

**Núcleo** (*core*) — a camada de regras puras, sem I/O. 100 % testável com `assert`.

---

## O

**Object mother** — função de fábrica que cria objetos de teste com valores padrão sensatos e
sobrescrita explícita.

**Oráculo** (*test oracle*) — o mecanismo que decide se a saída observada está correta. O
**problema do oráculo** é a dificuldade de tê-lo. Ver [10](10-fundamentos.md) §8.

---

## P

**Pairwise** (teste combinatório) — cobrir todos os **pares** de valores de parâmetros, em vez
de todas as combinações.

**Parametrização** — rodar o mesmo teste com vários conjuntos de dados
(`@pytest.mark.parametrize`, `it.each`).

**Partição de equivalência** — agrupar entradas que o programa trata igual e testar uma de
cada grupo.

**Pirâmide de testes** — muitos unitários, alguns de integração, poucos E2E. Proposta por
Mike Cohn (2009). Ver [12](12-tipos-e-piramide.md).

**Portas e adaptadores** (*ports and adapters*, hexagonal) — arquitetura em que o domínio
define as portas e a infraestrutura implementa os adaptadores.

**Propriedade (teste baseado em)** (*property-based testing*) — em vez de exemplos, enunciar
leis que devem valer para toda entrada, e deixar a biblioteca procurar o contraexemplo.

---

## Q

**Quarentena** — tirar um teste instável do portão de merge, **com prazo** para conserto.

---

## R

**Regressão** — defeito que reaparece, ou que surge por causa de uma mudança. **Teste de
regressão** é o que impede o retorno.

**Retry** (repetição) — reexecutar um teste que falhou. Analgésico, não cura.

**RIP** (*Reachability, Infection, Propagation*) — as três condições para uma falha ser
observada. Cobertura compra só a primeira.

**Rootdir** — o diretório-base que o pytest determina no início da execução. Aparece na
primeira linha da saída; leia-o quando algo estranho acontecer.

---

## S

**Sabotador** — dublê que falha de propósito, para exercitar o caminho triste. Não está na
taxonomia clássica, e é indispensável.

**Shrinking** — ver *encolhimento*.

**Smoke test** (teste de fumaça) — verificação mínima de que o sistema sobe e responde.

**Snapshot** — teste que compara a saída com uma cópia gravada. Útil para saída pequena e
estável; apodrece quando é grande.

**Spy** — dublê que registra as chamadas para o teste inspecionar depois.

**Stub** — dublê que devolve valores prontos. Não se verifica nada nele.

**Subsunção** — relação entre critérios de cobertura: satisfazer um implica satisfazer outro.
Não implica "acha mais bugs".

**SUT** (*system under test*) — o que está sendo testado.

**Suíte** (*test suite*) — o conjunto de testes de um projeto.

---

## T

**TDD** (*Test-Driven Development*) — escrever o teste antes do código, no ciclo
vermelho → verde → refatorar. Ver [15](15-tdd.md).

**Teardown** — a limpeza depois do teste.

**Teste de caracterização** (*characterization test*) — registra o comportamento **atual** de
um código, certo ou errado, para servir de rede antes de refatorar.

**Teste de contrato** — a mesma bateria rodando contra duas implementações do mesmo contrato
(fake e real). O antídoto para o fake mentiroso.

**Teste de contrato de consumidor** (*consumer-driven contract*, Pact) — o consumidor declara
o que espera; o produtor verifica isso no CI dele.

**Testing Trophy** — alternativa à pirâmide, proposta por Kent C. Dodds, com peso maior em
integração e a análise estática na base.

**Timeout** — tempo-limite de um teste ou de um job. Obrigatório em CI.

---

## U

**Unidade** — o alvo de um teste unitário. **Não há consenso** sobre o que é: função, classe,
módulo ou comportamento. Ver [13](13-teste-unitario-a-fundo.md).

**Unitário (teste)** — pela definição operacional deste curso: verifica um comportamento,
roda em milissegundos, não toca I/O e roda em qualquer ordem.

---

## V

**Valor de fronteira** (*boundary value*) — os defeitos moram nas bordas. Para cada fronteira,
teste o anterior, o exato e o seguinte.

**VCR** (*record & replay*) — gravar respostas HTTP reais e reproduzi-las nos testes
seguintes. Cuidado: filtre segredos antes de gravar.

**Verde / vermelho** — suíte passando / falhando.

---

## W

**Watch (modo)** — re-executar os testes automaticamente ao salvar um arquivo.

**WebDriver** — protocolo padronizado pelo W3C para automação de navegador.

---

## X

**xUnit** — a família de arcabouços descendentes do SUnit (1994): JUnit, PyUnit, NUnit,
PHPUnit, e todos os outros com a mesma anatomia.

**xfail** — marcar um teste como "espera-se que falhe". Com `strict=True`, o teste falha se
**passar** — o que avisa que o bug foi corrigido.

---

## Termos em inglês que se usam sem tradução

| Termo | O que é |
|---|---|
| *assert* | a asserção |
| *flaky* | instável |
| *hoisting* | içamento |
| *mock*, *stub*, *spy*, *fake* | os dublês |
| *runner* | corredor |
| *seam* | costura |
| *shrinking* | encolhimento |
| *smoke test* | teste de fumaça |
| *snapshot* | instantâneo |
| *watch mode* | modo de observação |

---

## Falsos amigos e confusões frequentes

| Confusão | Esclarecimento |
|---|---|
| **erro × defeito × falha** | engano humano × código incorreto × comportamento observável |
| **falso positivo** | em testes: teste **vermelho** sem bug. Diga qual convenção você usa. |
| **mock × dublê** | "mock" virou sinônimo coloquial de qualquer dublê; tecnicamente é um tipo específico |
| **cobertura × qualidade** | cobertura mede execução, não verificação |
| **integração** | dois sentidos: com dependência externa real, ou entre módulos seus |
| **`toBe` × `toEqual`** | identidade (`Object.is`) × estrutura |
| **`assert.equal` × `deepStrictEqual`** | valor × estrutura + protótipo |
| **TDD × testes automatizados** | TDD é uma disciplina de escrita; testes automatizados são o artefato |
| **QA × teste** | QA é qualidade como processo; teste é uma das atividades dentro dela |
| **teste unitário × teste rápido** | correlacionados, não sinônimos |
