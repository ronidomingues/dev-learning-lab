# 10 · Fundamentos

`Nível: iniciante → intermediário` · `Última atualização: 12/08/2026`

Este é o arquivo do vocabulário e dos modelos mentais. A partir daqui, todo termo usado no
curso já foi definido em algum lugar — a maioria, aqui.

---

## 1. Definição formal

> **Teste de software** é o processo de executar um programa com a intenção de encontrar
> defeitos.
> — Glenford Myers, *The Art of Software Testing* (1979)

Essa definição, de quase cinquenta anos, ainda é a melhor que existe, e a palavra crítica é
**intenção**. Um teste que você escreve esperando que passe não é um teste; é uma cerimônia.
Um teste é bom na medida em que **poderia** encontrar um defeito.

> **Teste automatizado** é um programa que executa outro programa com entradas conhecidas e
> compara o resultado observado com o resultado esperado, sem intervenção humana, produzindo
> um veredito binário.

Desdobrando os cinco elementos dessa frase:

| Elemento | Nome técnico | Perguntas que ele levanta |
|---|---|---|
| o programa executado | **SUT** — *system under test* | qual é a unidade? onde ela começa e acaba? |
| as entradas conhecidas | **dados de teste** | quais escolher? quantos bastam? |
| o resultado esperado | **oráculo** | **como você sabe qual é a resposta certa?** |
| a comparação | **asserção** | igualdade exata? tolerância? estrutura? |
| o veredito binário | **verde/vermelho** | e quando é "quase certo"? |

O terceiro é o mais profundo dos cinco, chama-se **problema do oráculo**, e é a razão pela
qual testar não é um problema resolvido. Voltamos a ele na seção 8 e em
[60-teoria-avancada.md](60-teoria-avancada.md).

---

## 2. Erro, defeito, falha: três palavras que não são sinônimos

A confusão entre elas causa discussão inútil em toda equipe. A terminologia abaixo é a do
padrão IEEE e é a que se usa em literatura séria.

```
 pessoa comete       vira uma linha        que, ao rodar,       que o usuário
    um ERRO      →     de código          produz uma          percebe como
   (engano)            DEFEITA             FALHA               PROBLEMA
                        (bug)             (comportamento
                                            errado)
```

| Termo | Inglês | O que é | Onde vive |
|---|---|---|---|
| **erro** | *error*, *mistake* | o engano humano | na cabeça de quem escreveu |
| **defeito** | *fault*, *defect*, *bug* | o trecho de código incorreto | no código-fonte |
| **falha** | *failure* | o comportamento observável errado | em tempo de execução |

**Por que a distinção importa na prática:**

1. **Nem todo defeito produz falha.** Um `if` errado num ramo que nunca é atingido é um
   defeito latente. Cobertura de código mede o esforço de *ativar* defeitos.
2. **Uma falha pode estar longe do defeito.** O `NullPointerException` na linha 400 vem de
   um campo não preenchido na linha 12. Por isso "onde falhou" ≠ "onde está o bug".
3. **Teste encontra falhas, não defeitos.** O teste diz "algo está errado"; achar o defeito
   é depuração, que é outra atividade.

**Para testar bem, é preciso um quarto conceito:** para uma falha ser observada, o defeito
precisa ser **executado**, precisa **corromper o estado**, e essa corrupção precisa
**propagar até a saída**. Isso se chama modelo **RIP** (*Reachability, Infection,
Propagation*), e explica por que 100% de cobertura não garante nada: cobertura só compra a
primeira das três condições.

---

## 3. As três partes de todo teste: Arrange–Act–Assert

Todo teste do mundo, em qualquer linguagem, tem esta forma:

```python
def test_desconto_de_dez_por_cento():
    preco = Dinheiro.de_reais("100,00")        # ARRANGE — prepare o cenário

    resultado = preco.aplicar_desconto(10)     # ACT — execute a ação, UMA

    assert resultado.centavos == 9000          # ASSERT — verifique
```

Nomes alternativos para a mesma coisa:

| Escola | Nomes |
|---|---|
| xUnit clássico | **Arrange · Act · Assert** (AAA) |
| BDD | **Given · When · Then** (Dado · Quando · Então) |
| Padrões de teste (Meszaros) | **Setup · Exercise · Verify · Teardown** (quatro fases) |

**Regras práticas que valem mais do que parecem:**

1. **Um único "Act" por teste.** Se há dois, você tem dois testes escondidos num só. Quando
   falhar, você não sabe qual ação quebrou.
2. **Separe as três partes visualmente** — uma linha em branco basta. Isso torna óbvio o
   teste que virou uma sopa de dez linhas.
3. **Se o "Arrange" tem 30 linhas, o problema não é o teste.** É o código, que exige um
   universo montado para funcionar. Ver
   [20-testabilidade-e-design.md](20-testabilidade-e-design.md).

A quarta fase, **Teardown**, é a limpeza. Em Python ela vive depois do `yield` da fixture;
em JavaScript, no `afterEach`. Em código bem desenhado (sem I/O), ela simplesmente não
existe.

---

## 4. O que é uma "unidade"?

Esta é a pergunta que mais gera briga no campo, e a resposta honesta é: **não há consenso**.

| Escola | A unidade é... | Consequência |
|---|---|---|
| **Clássica** (Detroit, Chicago) | um **comportamento**, que pode envolver várias classes | poucos dublês; testes mais robustos a refatoração |
| **Mockista** (Londres) | uma **classe**, isolada de todas as suas colaboradoras | muitos dublês; testes acoplados à estrutura |
| **Pragmática** (a mais comum hoje) | um **módulo/arquivo** com uma responsabilidade | meio-termo |

Kent Beck, que escreveu o primeiro framework xUnit, sempre defendeu a versão clássica.
Martin Fowler descreveu a disputa em *Mocks Aren't Stubs* (2007). Vladimir Khorikov, em
*Unit Testing* (2020), argumenta com dados que a escola clássica produz suítes mais
duráveis. Ver [13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md).

**A definição operacional que este curso adota**, e que evita a discussão sem perder o
essencial:

> Um teste é **unitário** se ele: (a) verifica **um comportamento**, (b) roda em
> **milissegundos**, (c) é **isolado** — não fala com banco, rede, disco, relógio ou outro
> processo — e (d) pode rodar em **qualquer ordem** junto com os outros.

Repare que a definição é sobre **propriedades observáveis do teste**, não sobre quantas
classes ele toca. Isso é proposital: as quatro propriedades é que produzem o benefício
(velocidade, diagnóstico preciso, confiança). O número de classes é acidente.

---

## 5. O teste como especificação executável

Este é o modelo mental mais produtivo do assunto todo.

Um teste é uma frase sobre o sistema, escrita numa linguagem que o computador verifica.

```python
def test_cliente_nao_paga_pelo_tempo_pausado():
    ...
```

Leia o nome: *"cliente não paga pelo tempo pausado"*. Isso é uma regra de negócio. Ela está
escrita num documento em algum lugar? Talvez. Aquele documento é verificado toda vez que
alguém muda o código? Não. **O teste é.**

Daí vêm três consequências práticas:

1. **O nome do teste é a parte mais importante dele.** Ele é o que você lê primeiro quando
   falha, e o que documenta a regra. `test_2` desperdiça isso.
2. **A lista de nomes de teste de um módulo é a especificação dele.** Rode
   `pytest --collect-only -q` e leia: se a lista não descreve o que o módulo faz, os testes
   estão nomeados errado.
3. **Testar algo que não é regra é desperdício.** `test_getter_devolve_o_campo` não
   especifica nada; só duplica o código.

---

## 6. Por que testes precisam ser rápidos, isolados e determinísticos

As três propriedades não são estética. Cada uma compra algo concreto.

### 6.1 Rápidos

O valor de uma suíte de testes é proporcional à **frequência** com que ela é rodada, e a
frequência cai brutalmente com o tempo de execução. A escala aproximada, do que se observa
em equipes reais:

| Tempo da suíte | Quando as pessoas rodam |
|---|---|
| < 1 s | a cada salvamento (modo *watch*) |
| < 10 s | a cada mudança significativa |
| < 2 min | antes de cada commit |
| < 10 min | antes do *push* |
| > 10 min | só no CI — e o CI vira o gargalo |
| > 1 h | ninguém espera; o time começa a ignorar o vermelho |

A última linha é a morte da suíte: quando a espera é longa demais, o time normaliza o
vermelho, e uma suíte com falhas normalizadas tem valor **negativo** — ela custa tempo de
manutenção e não dá sinal nenhum.

### 6.2 Isolados

Um teste não pode depender de outro. Se `test_b` só passa depois de `test_a` rodar, você
tem:

- impossibilidade de rodar um teste sozinho (adeus, laço rápido);
- impossibilidade de paralelizar;
- falhas em cascata: um teste quebra e vinte ficam vermelhos, escondendo a causa.

**Teste barato para descobrir se você tem isso:** rode a suíte em ordem aleatória
(`pytest-randomly`, `vitest --sequence.shuffle`). Se algo quebra, há acoplamento escondido.

### 6.3 Determinísticos

Mesma entrada, mesmo resultado, sempre. As quatro fontes de indeterminismo, em ordem de
frequência:

| Fonte | Sintoma | Solução |
|---|---|---|
| **relógio** | quebra à meia-noite, no fim do mês, em fevereiro | injete o relógio |
| **aleatoriedade** | quebra 1 vez em 50 | semente fixa, ou injete o gerador |
| **concorrência** | quebra sob carga, ou só no CI | evite; se precisar, sincronize explicitamente |
| **estado compartilhado** | quebra dependendo da ordem | isole (banco por teste, `tmp_path`) |

Um teste que às vezes passa e às vezes falha se chama ***flaky***, e é **pior do que não ter
teste nenhum** — porque ele treina o time a ignorar o vermelho. Tratamento em
[75-armadilhas.md](75-armadilhas.md).

---

## 7. Os cinco porquês: por que existe a pirâmide de testes?

Aplicando a regra dos cinco porquês a um dos conceitos centrais do campo.

**Afirmação:** deve-se ter muitos testes unitários, alguns de integração e poucos de ponta a
ponta.

**1. Por quê?** Porque testes de ponta a ponta são lentos e frágeis.

**2. Por que são lentos e frágeis?** Porque cada um sobe o sistema inteiro — navegador,
servidor, banco, fila — e depende de todos eles simultaneamente.

**3. Por que depender de tudo simultaneamente é frágil?** Porque a probabilidade de sucesso é
o **produto** das probabilidades de cada parte. Se cada uma das 5 partes funciona em 99,5 %
das execuções, o teste passa em 0,995⁵ ≈ **97,5 %** — ou seja, falha 1 vez em 40 **sem que
haja bug nenhum**. Com 200 testes desses, a chance de a suíte inteira passar limpa é
0,975²⁰⁰ ≈ **0,6 %**.

**4. Por que isso é fatal e não só chato?** Porque uma suíte que quase nunca fica verde
perde a propriedade que a torna útil: **vermelho significa problema**. O time passa a
reexecutar até passar ("*retry até verde*"), e a partir daí a suíte não detecta mais nada.

**5. Por que não simplesmente tornar cada parte mais confiável?** Porque uma parte é a rede,
outra é o navegador, outra é o agendador do sistema operacional — e você não controla
nenhuma delas. **Parada legítima: é uma restrição do mundo físico e da arquitetura
distribuída**, não uma falha de engenharia sua. A resposta possível é reduzir a *quantidade*
de testes expostos a ela, empurrando a verificação para camadas que você controla.

E aí está a pirâmide: ela não é uma preferência estética, é uma consequência aritmética de
confiabilidade composta. O desdobramento — incluindo as críticas legítimas à pirâmide e as
formas alternativas — está em [12-tipos-e-piramide.md](12-tipos-e-piramide.md).

---

## 8. O problema do oráculo

Como você sabe qual é a resposta certa?

Para `2 + 2`, é fácil. Para estes casos, não:

| Situação | Por que o oráculo é difícil |
|---|---|
| um compilador | qual é o "código de máquina certo"? só outro compilador saberia |
| um modelo de aprendizado de máquina | a saída correta é probabilística |
| um renderizador 3D | "a imagem está certa" é julgamento visual |
| um otimizador de rotas | você não conhece a rota ótima sem resolver o problema |
| uma simulação científica | é justamente o que você não sabe |

Elaine Weyuker chamou isso de **programas não-testáveis** em *On Testing Non-testable
Programs* (1982). Não significa que não se pode testá-los; significa que a asserção de
igualdade exata não está disponível, e é preciso outra estratégia:

| Estratégia | Ideia | Exemplo |
|---|---|---|
| **oráculo parcial** | verifique **propriedades**, não o valor | "a rota devolvida visita todas as cidades" |
| **teste metamórfico** | relacione **duas** execuções | "traduzir A→B→A deve preservar o sentido" |
| **oráculo de regressão** | compare com a versão anterior | teste de caracterização |
| **oráculo humano** | alguém olha | revisão visual, teste exploratório |
| **implementação de referência** | compare com outra implementação | seu `sort` vs. o da biblioteca |

Isso não é curiosidade acadêmica: o problema do oráculo é a razão pela qual testar sistemas
de IA em 2026 é uma área de pesquisa ativa, e não um exercício resolvido. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## 9. O que testes não podem fazer: o limite de Dijkstra

> "Testar programas pode ser usado para mostrar a presença de defeitos, mas nunca para
> mostrar a sua ausência."
> — Edsger W. Dijkstra, *Notes on Structured Programming* (1970)

A razão é combinatória, e é fácil de ver. Uma função que recebe dois inteiros de 64 bits tem
2¹²⁸ ≈ 3,4 × 10³⁸ entradas possíveis. Testando um bilhão por segundo, você levaria mais que
a idade do universo — muitas vezes.

Testar é, portanto, **amostragem**. E a pergunta central da teoria de testes vira: *que
amostra dá mais informação por unidade de esforço?* As respostas práticas:

| Técnica | Ideia | Onde está |
|---|---|---|
| **partição de equivalência** | agrupe entradas que o código trata igual; teste uma de cada | seção 10 |
| **valores de fronteira** | os bugs moram nas bordas dos grupos | seção 10 |
| **teste de propriedades** | deixe a máquina amostrar, com invariantes | [exemplo 5](06-exemplos.md) |
| **teste combinatório (*pairwise*)** | cubra todo par de parâmetros, não toda combinação | [60](60-teoria-avancada.md) |
| **análise de mutação** | avalie a suíte injetando defeitos artificiais | [19](19-cobertura-e-metricas.md) |
| **verificação formal** | prove, em vez de amostrar | [60](60-teoria-avancada.md) |

---

## 10. Escolher os casos: partição e fronteira

As duas técnicas de maior retorno por esforço em toda a engenharia de testes. Aprenda estas
duas e você já testa melhor que a média.

### 10.1 Partição de equivalência

Agrupe as entradas em classes que o programa **trata do mesmo jeito**. Teste **uma** de cada
classe; testar mais é desperdício.

Exemplo — desconto por faixa de idade:

```
idade < 0      → inválido
0 ≤ idade < 12 → 50% de desconto
12 ≤ idade < 60 → sem desconto
idade ≥ 60     → 30% de desconto
idade > 130    → inválido (suspeito)
```

Cinco classes → cinco testes bastam para a "parte de dentro" de cada faixa. Testar 5, 6, 7,
8, 9 e 10 anos é testar a mesma coisa seis vezes.

### 10.2 Valores de fronteira

Os defeitos moram **nas bordas** — porque `<` versus `<=` é o erro mais cometido da
programação. Para cada fronteira, teste **três** valores: o anterior, o exato, o seguinte.

| Fronteira | Testar |
|---|---|
| 12 anos | 11, **12**, 13 |
| 60 anos | 59, **60**, 61 |
| 0 | −1, **0**, 1 |
| frete grátis a partir de R$ 200 | 19999, **20000**, 20001 centavos |
| lista | vazia, **um elemento**, dois, muitos |
| texto | `""`, um caractere, no limite, acima do limite |

Repare que o valor **exato** da fronteira é o único que distingue `>=` de `>`. Se você testar
só 100 e 300 numa regra "a partir de 200", tanto faz qual operador está no código — e o teste
não testa nada da fronteira.

**Caso especial que quase todo mundo esquece:** entradas vazias, nulas e "de tamanho um".
Lista vazia, string vazia, `None`/`null`, zero, e o caso com exatamente um elemento (onde
laços com `i < n-1` quebram).

---

## 11. Vocabulário essencial

Definições curtas; as completas estão no [GLOSSARIO.md](GLOSSARIO.md).

| Termo | Definição |
|---|---|
| **SUT** | *system under test* — o que está sendo testado |
| **asserção** | afirmação verificada; se falsa, o teste falha |
| **fixture** | cenário preparado antes do teste; também o mecanismo que o prepara |
| **suíte** | conjunto de testes |
| **corredor** (*runner*) | o programa que descobre, executa e reporta os testes (pytest, `node:test`) |
| **dublê** (*test double*) | objeto falso que substitui uma dependência real |
| **cobertura** | fração do código executada pelos testes |
| **regressão** | defeito que reaparece, ou que surge por causa de uma mudança |
| **teste de regressão** | teste escrito para impedir que um bug volte |
| **flaky** | teste que passa e falha sem que nada mude |
| **verde / vermelho** | suíte passando / falhando |
| **CI** | *continuous integration* — o robô que roda a suíte a cada envio |
| **TDD** | escrever o teste antes do código |
| **falso positivo** | teste falha, mas o código está certo (teste ruim) |
| **falso negativo** | teste passa, mas o código está errado (teste inútil) |

> **Cuidado com "falso positivo".** Em testes, a convenção usual é: *positivo* = teste
> acusou problema. Então **falso positivo = teste vermelho sem bug**. Em medicina e em
> segurança a convenção é a mesma; em estatística, o "positivo" às vezes é o oposto. Quando
> a conversa começar a girar em círculos, é quase sempre por isso — diga qual convenção você
> está usando.

---

## 12. Os quatro pilares de uma boa suíte

Um modelo de Vladimir Khorikov (*Unit Testing: Principles, Practices, and Patterns*, 2020)
que este curso adota porque explica **trade-offs**, não só boas intenções.

| Pilar | O que é | Como se perde |
|---|---|---|
| **Proteção contra regressão** | o teste pega bugs de verdade | testes triviais (getters, mocks testando mocks) |
| **Resistência a refatoração** | o teste **não** quebra quando o código muda sem mudar comportamento | testar detalhe de implementação, excesso de mocks |
| **Retorno rápido** | roda em milissegundos | I/O, dependências reais, setup pesado |
| **Manutenibilidade** | fácil de ler e de mudar | fixtures em cascata, mocks complexos, nomes ruins |

A tese central, e o motivo de o modelo ser útil: **os três primeiros são mutuamente
excludentes — você só pode maximizar dois.**

- Teste de ponta a ponta: proteção alta ✅, resistência alta ✅, **rapidez péssima** ❌
- Teste unitário trivial: rapidez ✅, resistência ✅, **proteção nula** ❌
- Teste com muitos mocks: rapidez ✅, proteção média, **resistência péssima** ❌

Por isso não existe "o jeito certo de testar", e sim uma **carteira** de testes com
proporções escolhidas conforme o risco de cada parte do sistema. E por isso a discussão
"unitário vs. integração" nunca termina: as duas escolas estão otimizando pilares
diferentes.

**O pilar mais subestimado é a resistência a refatoração.** Uma suíte que quebra a cada
mudança interna treina o time a apagar testes, e é assim que a suíte morre — não de uma vez,
mas por erosão.

---

## 13. Como isso tudo se encaixa

```
                     ┌───────────────────────────────────┐
                     │  o que se quer: confiança para     │
                     │  mudar o código sem medo           │
                     └────────────────┬──────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
 ┌──────▼───────┐           ┌─────────▼─────────┐        ┌──────────▼────────┐
 │  ESCOLHER    │           │     ESCREVER      │        │      RODAR        │
 │  o que testar│           │     o teste       │        │    o tempo todo   │
 ├──────────────┤           ├───────────────────┤        ├───────────────────┤
 │ partição     │           │ Arrange-Act-Assert│        │ localmente (watch)│
 │ fronteira    │           │ nome = regra      │        │ antes do commit   │
 │ pirâmide     │           │ dublês, quando    │        │ no CI             │
 │ risco        │           │   preciso         │        │ rápido, senão     │
 │ oráculo      │           │ 1 comportamento   │        │   ninguém roda    │
 └──────┬───────┘           └─────────┬─────────┘        └──────────┬────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                     ┌────────────────▼──────────────────┐
                     │  o que ATRAPALHA: código difícil   │
                     │  de testar. A solução é mudar o    │
                     │  CÓDIGO, não a ferramenta.         │
                     │        → cap. 20                   │
                     └───────────────────────────────────┘
```

---

## Autoteste

1. Qual é a palavra crítica na definição de Myers, e por quê?
2. Diferencie erro, defeito e falha, com um exemplo de cada.
3. O que é o modelo RIP e o que ele explica sobre cobertura de código?
4. Escreva as três fases de um teste e diga o que indica um "Arrange" de 30 linhas.
5. Dê a definição operacional de teste unitário adotada por este curso, com as quatro propriedades.
6. Por que uma suíte que leva uma hora tem valor **negativo**?
7. Faça a conta: 5 componentes, cada um confiável em 99,5 %. Qual a taxa de falso vermelho de um teste de ponta a ponta?
8. O que é o problema do oráculo? Cite dois sistemas onde ele aparece com força.
9. Enuncie a frase de Dijkstra e explique por que ela é uma consequência combinatória.
10. Numa regra "desconto a partir de 60 anos", quais três valores você testa e por quê?
11. Quais são os quatro pilares de Khorikov, e qual a tese central sobre eles?
12. Por que a resistência a refatoração é o pilar mais subestimado?
