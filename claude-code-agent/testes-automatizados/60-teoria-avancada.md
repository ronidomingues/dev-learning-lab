# 60 · Teoria avançada

`Nível: pesquisa` · `Última atualização: 13/08/2026`

Aqui o assunto deixa de ser "como usar pytest" e passa a ser "o que é possível saber sobre
um programa executando-o". As referências completas estão em
[95-referencias.md](95-referencias.md).

---

## 1. Testar é decidir um problema indecidível — e por isso não dá

### 1.1 O resultado fundamental

Considere a pergunta: *"este programa está correto em relação a esta especificação?"*

Para programas em uma linguagem Turing-completa, essa pergunta é **indecidível**. A redução é
imediata a partir do problema da parada: se existisse um algoritmo `CORRETO(P, S)`, poderíamos
construir a especificação "P termina" e decidir a parada — o que Turing provou impossível em
1936.

O **teorema de Rice** (1953) generaliza: *qualquer* propriedade semântica não trivial de
programas é indecidível. "Não trivial" quer dizer que vale para alguns programas e não para
outros. "Está correto", "nunca acessa índice inválido", "sempre termina" — todas indecidíveis.

### 1.2 O que isso implica para a prática

| Implicação | Consequência concreta |
|---|---|
| não existe teste completo | testar é **amostrar** |
| não existe gerador de teste perfeito | toda ferramenta de geração é heurística |
| não existe métrica computável de "suíte boa" | cobertura e mutação são aproximações |
| análise estática perfeita não existe | todo linter tem falso positivo ou falso negativo |

Não é pessimismo: é o mesmo motivo pelo qual a engenharia estrutural usa fatores de
segurança em vez de provar que a ponte nunca cai. **Você trabalha com aproximações
justificadas, não com certeza.**

### 1.3 A saída parcial: restringir a linguagem

Se o poder computacional é o problema, tire poder. É o que fazem:

- **linguagens totais** (Agda, Idris, Dhall): toda função termina, por construção;
- **sistemas de tipos ricos**: transferem parte da verificação para a compilação;
- **subconjuntos verificáveis** (SPARK Ada, MISRA C): proibições que tornam a análise decidível;
- **linguagens de consulta declarativas**: SQL sem recursão é decidível.

Trade-off explícito: **expressividade × verificabilidade**. Você não pode ter as duas ao
máximo.

---

## 2. O problema do oráculo

### 2.1 Enunciado

Dado um programa `P` e uma entrada `x`, como decidir se `P(x)` é a saída correta?

Elaine Weyuker, em *On Testing Non-testable Programs* (1982), chamou de **não-testáveis** os
programas em que (a) não existe oráculo, ou (b) é caro demais determinar a resposta correta.
Exemplos: compiladores, simulações científicas, otimizadores, sistemas de aprendizado de
máquina, renderizadores.

### 2.2 Oráculos parciais

| Tipo | Ideia | Exemplo |
|---|---|---|
| **especificado** | a resposta é conhecida | `2 + 2 == 4` |
| **derivado** | compara com implementação de referência | seu `sort` × `sorted()` |
| **de propriedade** | verifica invariantes | `len(sort(x)) == len(x)` e é ordenado |
| **metamórfico** | relaciona duas execuções | `sort(shuffle(x)) == sort(x)` |
| **de regressão** | compara com a versão anterior | teste de caracterização |
| **estatístico** | verifica distribuição | um gerador aleatório passa em testes de uniformidade |
| **humano** | alguém julga | teste exploratório, revisão visual |

### 2.3 Teste metamórfico

Proposto por T. Y. Chen em 1998. A ideia: mesmo sem saber a resposta certa, você conhece
**relações** entre execuções.

```python
# Não sei qual é a distância mais curta entre A e B.
# Mas sei que:
def test_relacao_metamorfica_simetria():
    assert rota(A, B).distancia == rota(B, A).distancia

def test_relacao_metamorfica_desigualdade_triangular():
    assert rota(A, C).distancia <= rota(A, B).distancia + rota(B, C).distancia

def test_relacao_metamorfica_invariancia_a_rotulos():
    """Renomear as cidades não pode mudar a distância."""
    assert rota(A, B).distancia == rota(renomear(A), renomear(B)).distancia
```

É a técnica dominante para testar sistemas em que a saída correta é desconhecida — busca,
tradução automática, compiladores (compilar com `-O0` e `-O2` deve dar o mesmo resultado
observável), e modelos de aprendizado de máquina.

---

## 3. Teoria da adequação de critérios

### 3.1 O trabalho fundador

Goodenough & Gerhart, *Toward a Theory of Test Data Selection* (1975), formalizaram o que
seria um critério de teste **confiável** e **válido**:

- **confiável** (*reliable*): se um conjunto de teste que satisfaz o critério passa, todos os
  outros que o satisfazem também passam;
- **válido** (*valid*): se o programa tem um defeito, algum conjunto que satisfaz o critério
  o revela.

O resultado central: um critério **confiável e válido** decidiria a correção — logo, pelo
teorema de Rice, **não pode existir** em geral. Todos os critérios práticos abrem mão de uma
das propriedades.

### 3.2 A hierarquia de subsunção

Um critério **subsome** outro se satisfazê-lo implica satisfazer o outro.

```
        caminho
           │
     caminho-prime
           │
        MC-DC
           │
    condição/decisão
       │        │
    ramo      condição
       │
      linha
```

**Cuidado com a leitura ingênua:** subsunção diz respeito ao *critério*, não à *capacidade de
achar bugs*. Existem resultados empíricos mostrando que um conjunto de testes que satisfaz um
critério mais forte não necessariamente encontra mais defeitos que outro conjunto que
satisfaz um critério mais fraco — porque a **força das asserções** é uma variável
independente, e a subsunção não a captura.

### 3.3 A crítica de Hamlet

Richard Hamlet e Ross Taylor, em *Partition Testing Does Not Inspire Confidence* (1990),
mostraram formalmente que o teste por partição só supera o teste aleatório quando as
partições são **realmente homogêneas** em relação a falha — e determinar isso exige
conhecer os defeitos, que é o que se quer descobrir.

**Conclusão prática, incômoda e honesta:** a superioridade da partição sobre a amostragem
aleatória depende da qualidade do seu modelo do domínio. Quando você **entende** o problema,
partição é muito melhor. Quando você não entende, o teste aleatório (fuzzing, propriedades)
tende a ser mais produtivo — o que explica por que as duas técnicas coexistem em vez de uma
substituir a outra.

---

## 4. Análise de mutação: as duas hipóteses

Introduzida por DeMillo, Lipton & Sayward em *Hints on Test Data Selection* (1978). A
validade da técnica se apoia em duas hipóteses empíricas:

### 4.1 Hipótese do programador competente

> Programadores escrevem programas **quase** corretos. Os defeitos reais são pequenos desvios
> sintáticos de um programa correto.

Se ela vale, mutar o programa com pequenas alterações gera algo próximo dos defeitos reais.

**Evidência:** estudos de defeitos reais em repositórios mostram que a maioria das correções
é pequena (poucas linhas). **Limite:** defeitos de **omissão** — a lista vazia que ninguém
tratou, a condição que falta — não são gerados por mutação, porque não há código para mutar.
Essa é a mesma cegueira da cobertura ([19](19-cobertura-e-metricas.md) §3.2).

### 4.2 Efeito de acoplamento

> Uma suíte capaz de detectar todos os defeitos **simples** também detecta a maioria dos
> defeitos **complexos** (combinações de vários simples).

**Evidência:** experimentos de Offutt (1992) e replicações posteriores sustentam a hipótese
para as combinações estudadas. Não é um teorema.

### 4.3 O problema dos mutantes equivalentes

Um mutante **equivalente** é sintaticamente diferente e semanticamente idêntico:

```python
for i in range(len(lista)):        # original
for i in range(0, len(lista)):     # mutante equivalente — nenhum teste pode matá-lo
```

Decidir se um mutante é equivalente é **indecidível** (é decidir equivalência de programas).
Na prática, isso significa que o escore de mutação tem um **teto desconhecido** abaixo de
100 %, e que parte do tempo de análise é gasta examinando mutantes que ninguém poderia matar.

Mitigações usadas em ferramentas modernas: heurísticas de detecção, **mutação seletiva**
(subconjunto de operadores com boa relação custo-benefício) e **mutantes de ordem superior**.

---

## 5. Teste baseado em propriedades: a máquina por dentro

### 5.1 Origem

**QuickCheck** (Claessen & Hughes, ICFP 2000), em Haskell. Três ideias:

1. o teste é uma **propriedade** universalmente quantificada;
2. **geradores** produzem valores aleatórios do tipo certo;
3. ao falhar, o **encolhimento** (*shrinking*) reduz o contraexemplo ao menor que ainda falha.

### 5.2 Encolhimento

É o que separa a técnica de "fuzzing com asserção". Um contraexemplo de 4 KB é inútil; um
contraexemplo `total=1, n=2` é uma explicação.

Duas famílias de implementação:

| Abordagem | Como | Problema |
|---|---|---|
| **encolhimento por tipo** (QuickCheck clássico) | cada gerador sabe encolher o seu tipo | quebra invariantes ("encolheu" para um valor inválido) |
| **encolhimento integrado** (Hypothesis, Hedgehog) | encolhe o **fluxo de bytes** que alimentou o gerador | preserva os invariantes por construção |

A Hypothesis usa a segunda, e é por isso que os contraexemplos dela quase sempre continuam
válidos. Ela também **guarda a base de dados** de contraexemplos (`.hypothesis/`) e os
reexecuta primeiro nas próximas execuções — o que dá regressão automática.

### 5.3 Máquinas de estado com propriedades

O uso mais poderoso da técnica: a biblioteca gera **sequências** de operações e verifica
invariantes ao final.

```python
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule


class MaquinaDeAssinatura(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.a = Assinatura.criar("a1", "ana@ex.br", CATALOGO["pro"], HOJE)

    @rule()
    def pausar(self):
        with contextlib.suppress(TransicaoInvalida):
            self.a.pausar()

    @rule()
    def falhar(self):
        with contextlib.suppress(TransicaoInvalida):
            self.a.registrar_falha()

    @invariant()
    def tentativas_dentro_do_limite(self):
        assert 0 <= self.a.tentativas_falhas <= MAX_TENTATIVAS

    @invariant()
    def ativa_implica_sem_falhas(self):
        if self.a.estado is Estado.ATIVA:
            assert self.a.tentativas_falhas == 0
```

Isso encontra sequências que nenhum humano escreveria — e é onde bugs de máquina de estado
realmente moram. É a versão "com shrinking" do teste de invariantes do projeto-modelo.

### 5.4 O limite

Propriedades encontram o que você conseguiu **enunciar como lei**. Se a regra de negócio é
"clientes do Norte pagam frete diferente", nenhuma propriedade genérica vai descobrir isso.
Propriedades e exemplos são complementares, não substitutos.

---

## 6. Teste combinatório

### 6.1 O problema

10 parâmetros booleanos = 1024 combinações. 10 parâmetros com 5 valores = ~9,7 milhões.

### 6.2 A observação empírica

Estudos do NIST (Kuhn, Wallace, Gallo, ~2004) sobre defeitos reais em vários domínios
encontraram que a grande maioria dos defeitos é disparada pela interação de **poucos**
parâmetros — a maior parte por 1 ou 2, e praticamente todos por 6 ou menos. É a **hipótese da
interação de poucos fatores**.

### 6.3 Consequência: cobertura *pairwise*

Se basta cobrir todos os **pares** de valores, o número de casos cai drasticamente. Para 10
parâmetros com 5 valores cada, um conjunto *pairwise* costuma ter algumas dezenas de casos em
vez de milhões.

```python
# pip install allpairspy
from allpairspy import AllPairs

CASOS = list(AllPairs([
    ["SP", "AM", "RS"],                # uf
    ["pix", "cartao", "boleto"],       # pagamento
    [True, False],                     # cliente novo
    ["basico", "pro", "anual"],        # plano
]))
# 3 × 3 × 2 × 3 = 54 combinações → ~9 casos cobrindo todos os pares

@pytest.mark.parametrize(("uf", "pagamento", "novo", "plano"), CASOS)
def test_checkout(uf, pagamento, novo, plano): ...
```

**Limite honesto:** *pairwise* é um argumento de **cobertura**, não de correção. Se a sua
regra depende de uma interação de três fatores, o conjunto de pares pode não a exercitar.

---

## 7. Fuzzing

### 7.1 As gerações

| Geração | Técnica | Exemplo |
|---|---|---|
| **cega** (Miller, 1990) | bytes aleatórios na entrada | derrubou ~1/3 dos utilitários Unix da época |
| **guiada por gramática** | gera entradas sintaticamente válidas | *fuzzers* de JSON, SQL, JS |
| **guiada por cobertura** | mede cobertura e favorece entradas que abrem caminho novo | AFL, libFuzzer, `atheris` |
| **simbólica / concólica** | resolve restrições para atingir ramos específicos | KLEE, SAGE |

O salto de qualidade foi o terceiro: o *fuzzer* guiado por cobertura faz uma busca evolutiva
no espaço de entradas, usando a cobertura como função de aptidão.

### 7.2 Fuzzing e teste de propriedades são parentes

| | Teste de propriedades | Fuzzing |
|---|---|---|
| entrada | gerada **tipada**, por estratégia | bytes, ou gramática |
| oráculo | a propriedade que você escreveu | quase sempre "não travar" |
| objetivo | correção lógica | robustez e segurança |
| encolhimento | central | existe, menos elaborado |

A Hypothesis pode ser guiada por cobertura, e o `atheris` (Google) integra libFuzzer com
Python. A fronteira entre as duas técnicas praticamente desapareceu.

### 7.3 Fuzzing contínuo

O **OSS-Fuzz** roda *fuzzers* continuamente em centenas de projetos de código aberto e já
reportou dezenas de milhares de defeitos. Isso mudou o campo: fuzzing deixou de ser
"atividade de auditoria" e virou **infraestrutura permanente**, com corpus que cresce e
regressões automáticas.

---

## 8. Onde teste encontra verificação formal

| Técnica | Garante | Custo | Onde se usa |
|---|---|---|---|
| teste | os casos executados | baixo | em todo lugar |
| análise estática | ausência de certas classes de erro | baixo | linters, tipos |
| interpretação abstrata | ausência de erro de execução, com aproximação | médio | Astrée (aviônica), Infer |
| verificação de modelo | propriedades temporais em um modelo finito | alto | TLA+, SPIN, protocolos |
| prova de teoremas | correção total | altíssimo | seL4, CompCert |

**A relação prática:** a verificação formal **não substitui** o teste. Ela prova que a
implementação satisfaz a **especificação**; se a especificação estiver errada, a prova está
certa e o sistema está errado. O caso do seL4 (micronúcleo verificado) é exemplar: a prova
cobre a implementação, e o time continua testando os pressupostos sobre o hardware.

**Onde a fronteira está se movendo em 2026:** verificação leve embutida em linguagens de uso
geral — tipos refinados, contratos verificados estaticamente, e ferramentas que provam
ausência de *overflow* ou de acesso fora de limites em subconjuntos práticos.

---

## 9. Geração automática de testes

### 9.1 Busca (*search-based*)

**EvoSuite** (Java) e **Pynguin** (Python) usam algoritmos evolutivos: a função de aptidão é
a cobertura, e o algoritmo evolui suítes que a maximizam.

**O problema fundamental, que a técnica não resolve:** ela gera **entradas**, não
**oráculos**. Sem saber o que é correto, a ferramenta só pode escrever asserções que
registram o comportamento **atual** — que é útil como teste de caracterização e inútil para
achar bugs existentes.

### 9.2 Modelos de linguagem

A partir de ~2023, LLMs passaram a gerar testes que compilam, rodam e às vezes até fazem
asserções sensatas — porque aprenderam a intenção do código a partir de nomes, tipos,
comentários e testes semelhantes.

**O que a literatura de 2025–2026 vem reportando** (ver
[65-estado-da-arte.md](65-estado-da-arte.md) e
[95-referencias.md](95-referencias.md)):

- ganhos reais de cobertura em relação a técnicas puramente evolutivas em alguns domínios;
- **taxas altas de falha de compilação** por alucinação de símbolos e de APIs inexistentes,
  variando enormemente entre modelos e estratégias de prompt;
- **problemas de manutenibilidade** nos testes gerados — números mágicos, muitas asserções
  sem foco (*assertion roulette*);
- melhora significativa com estratégias de raciocínio estruturado e com verificação de
  execução no laço.

**O que continua não resolvido, e é conceitual:** o **oráculo**. Um modelo infere a intenção
a partir do código — e se o código estiver errado, ele infere a intenção errada e escreve o
teste que aprova o bug. É a mesma limitação de escrever testes depois, automatizada e em
escala. Nenhum avanço de modelo resolve isso, porque a informação **não está** no artefato.

---

## 10. Limites de tempo e a economia da verificação

Um resultado desconfortável e útil: o esforço de teste tem **retornos decrescentes**.

Modelos de crescimento de confiabilidade (Musa, Goel-Okumoto) descrevem a taxa de descoberta
de defeitos como decaindo aproximadamente de forma exponencial com o esforço. Consequências:

1. **os primeiros testes têm retorno enorme** — os caminhos principais concentram os defeitos
   de maior frequência;
2. **os últimos têm retorno quase nulo** — o caminho que só é atingido em 1 de 10⁶ execuções;
3. **existe um ponto ótimo econômico** de esforço, e ele **não** é "cobertura total";
4. o ponto ótimo depende do **custo da falha** — o que explica por que o marca-passo e o
   agregador de memes têm níveis de teste diferentes, e ambos estão certos.

Formulação prática: teste na proporção de **consequência da falha × probabilidade da falha**,
e aceite explicitamente o risco residual. Uma organização madura **escreve** qual é o risco
residual aceito; uma imatura finge que ele é zero.

---

## Autoteste

1. Enuncie o teorema de Rice e derive dele uma consequência prática para testes.
2. Qual é a saída parcial para a indecidibilidade, e qual trade-off ela impõe?
3. Defina o problema do oráculo e cite três tipos de oráculo parcial.
4. Escreva duas relações metamórficas para uma função de busca de rota.
5. O que Goodenough & Gerhart definiram como critério confiável e válido, e por que não pode existir?
6. Por que a hierarquia de subsunção não implica "acha mais bugs"?
7. Enuncie a crítica de Hamlet ao teste por partição e a consequência prática.
8. Quais são as duas hipóteses da análise de mutação, e qual defeito ela não gera?
9. O que é um mutante equivalente e por que ele não pode ser detectado automaticamente?
10. Diferencie encolhimento por tipo e encolhimento integrado. Qual a vantagem do segundo?
11. Enuncie a hipótese da interação de poucos fatores e o que ela justifica.
12. Qual é o limite conceitual da geração automática de testes que nenhum modelo resolve?
13. Por que verificação formal não substitui teste?
14. Explique os retornos decrescentes do esforço de teste e o que determina o ponto ótimo.
