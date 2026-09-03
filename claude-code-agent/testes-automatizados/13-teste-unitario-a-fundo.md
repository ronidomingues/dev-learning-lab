# 13 · Teste unitário a fundo

`Nível: intermediário → avançado` · `Última atualização: 12/08/2026`

Este é o arquivo que responde diretamente à pergunta *"o que são testes unitários?"* — mas
com a profundidade que a pergunta merece, e não com a definição de uma linha que circula por
aí.

---

## 1. A definição de uma linha, e por que ela é insuficiente

> "Teste unitário é o teste de uma unidade isolada de código."

Está certa e não serve para nada, porque as duas palavras que importam — **unidade** e
**isolada** — não estão definidas, e é justamente nelas que mora um debate de 26 anos.

---

## 2. O que é uma "unidade"?

### 2.1 As respostas em disputa

| Resposta | Quem defende | Consequência prática |
|---|---|---|
| **uma função** | tradição procedural | testes muito granulares; muitos triviais |
| **uma classe** | escola de Londres (mockista) | toda colaboradora vira mock |
| **um comportamento** | escola clássica (Beck, Fowler, Khorikov) | vários objetos reais num teste só |
| **um módulo/arquivo** | pragmatismo moderno | meio-termo, e o mais comum na prática |

### 2.2 O experimento mental que resolve a questão

Considere:

```python
def total(carrinho: Carrinho) -> Dinheiro:
    return subtotal(carrinho) + frete(carrinho)
```

Um teste de `total` chama `subtotal` e `frete` de verdade. **Isso é teste unitário?**

- Escola mockista: **não** — você deveria mockar `subtotal` e `frete`.
- Escola clássica: **sim** — `subtotal` e `frete` são detalhes internos do comportamento
  "calcular o total". O teste verifica o comportamento; se ele é implementado por uma função
  ou por três, é irrelevante.

Agora aplique o teste decisivo: **se eu inlinar `subtotal` dentro de `total`, o teste
quebra?**

- Na versão clássica: **não**. O teste continua verde. ✅
- Na versão mockista: **sim**, catastroficamente — o mock de `subtotal` nunca é chamado. ❌

O teste que quebra quando o comportamento **não** mudou está errado. Isso é a
**resistência a refatoração**, um dos quatro pilares de
[10-fundamentos.md](10-fundamentos.md) §12, e é o argumento mais forte a favor da escola
clássica.

### 2.3 Onde a escola mockista está certa

Não é uma escola errada; ela otimiza outra coisa. Ela está certa quando:

- **A colaboradora é uma dependência externa** (banco, rede, e-mail, pagamento). Aí você
  **precisa** de um dublê, e a discussão acaba.
- **O efeito colateral é o comportamento.** "Enviar o e-mail de confirmação" não deixa rastro
  no estado do sistema; a única forma de verificar é olhar a chamada.
- **Você está fazendo *outside-in* TDD.** Você escreve o teste da camada de fora antes de as
  camadas de dentro existirem, e os mocks são os *"eu ainda não escrevi isso"*. Depois eles
  costumam ser substituídos por objetos reais. Esse é o método de Freeman & Pryce em
  *Growing Object-Oriented Software, Guided by Tests* (2009), e ele é coerente.

### 2.4 A regra prática que este curso adota

> **Mocke apenas o que atravessa a fronteira do seu processo** — banco, rede, sistema de
> arquivos, relógio, aleatoriedade, fila, e serviços de terceiros.
> **Nunca mocke o seu próprio domínio.**

Essa regra é fácil de aplicar, produz suítes duráveis, e coincide com o que Khorikov chama
de "dependências fora do processo" versus "dependências dentro do processo".

---

## 3. O que é "isolado"?

Três sentidos, frequentemente confundidos:

| Sentido | Significa | Precisa? |
|---|---|---|
| **isolado de dependências** | não toca banco/rede/disco/relógio | **sim** |
| **isolado de outros testes** | roda em qualquer ordem, sem estado compartilhado | **sim, sempre** |
| **isolado de outras classes suas** | toda colaboradora é um dublê | **não** |

Os dois primeiros são inegociáveis. O terceiro é a escolha de escola, e a resposta deste
curso é "não".

**Por que o segundo é inegociável:** sem ele você perde a capacidade de rodar um teste
sozinho, de paralelizar, e de confiar no diagnóstico. E a violação é fácil de introduzir sem
perceber:

```python
# ARMADILHA: lista no nível do módulo, compartilhada entre testes
PEDIDOS = []

def test_a():
    PEDIDOS.append(1)
    assert len(PEDIDOS) == 1     # passa

def test_b():
    PEDIDOS.append(2)
    assert len(PEDIDOS) == 1     # falha — a menos que test_a não tenha rodado
```

```javascript
// ARMADILHA em JavaScript: o módulo é um singleton
// config.js
export const config = { modo: 'producao' };

// teste 1 faz config.modo = 'teste' e nunca desfaz.
// Todo teste seguinte vê 'teste'. Nada avisa.
```

**Como descobrir se você tem isso:** rode em ordem aleatória.

```bash
pip install pytest-randomly && pytest        # embaralha por padrão
npx vitest run --sequence.shuffle
```

---

## 4. Anatomia de um bom teste unitário

```python
def test_gateway_fora_do_ar_nao_pune_o_cliente(self):
    """A distinção mais importante deste serviço.

    "Cartão recusado" é culpa do cliente e conta tentativa.
    "Gateway caiu" é culpa nossa e NÃO conta.
    """
    servico, repo, _g, espiao = montar(vencida("a1", "ana@ex.br"),
                                       gateway=GatewayQueExplode())

    relatorio = servico.renovar_vencidas()

    salva = repo.buscar("a1")
    assert relatorio.com_erro == 1
    assert salva.tentativas_falhas == 0
    assert salva.estado is Estado.ATIVA
```

Sete propriedades, cada uma com uma razão:

| Propriedade | Razão |
|---|---|
| **nome descreve a regra de negócio** | é o que você lê primeiro quando falha às 23h |
| **docstring explica *por que* a regra existe** | o "o quê" está no código; o "porquê" se perde |
| **cenário montado por uma função** (`montar`) | o teste mostra o que é *relevante*, não o boilerplate |
| **um único "Act"** | quando falha, você sabe qual ação quebrou |
| **verifica estado, não interação** | resiste a refatoração |
| **três asserções sobre o mesmo comportamento** | asserções complementares, não comportamentos diferentes |
| **nenhum I/O** | roda em microssegundos |

### 4.1 "Uma asserção por teste"? Não.

A regra "um `assert` por teste" é repetida à exaustão e é uma **simplificação ruim**. O
correto é:

> **Um *comportamento* por teste.** Ele pode precisar de três asserções para ser descrito.

O teste acima tem três `assert`, e as três descrevem **um** comportamento: "falha de
infraestrutura não pune o cliente". Separá-las em três testes triplicaria o setup sem
ganhar diagnóstico.

O que é ruim de verdade é isto:

```python
def test_assinatura():           # ← *assertion roulette*
    assert a.estado is ATIVA
    assert a.pausar() is None
    assert a.estado is PAUSADA
    assert a.cancelar() is None
    assert a.estado is CANCELADA
```

Aqui há **três** comportamentos. A primeira asserção que falhar interrompe o teste, e você
descobre os problemas um por vez, numa série de execuções.

---

## 5. O que NÃO testar

Testar demais custa mais do que parece: cada teste é código a manter, e testes triviais são
puro passivo.

| Não teste | Por quê |
|---|---|
| **getters e setters** | não há lógica; o teste duplica o código |
| **a biblioteca padrão** | `sorted()` funciona; se não funcionasse, você teria outro problema |
| **framework de terceiros** | não é seu; teste a **sua** integração com ele |
| **detalhes privados** | mudam sem mudar comportamento; o teste vira lastro |
| **configuração declarativa** | testar que `TIMEOUT = 30` é `30` não diz nada |
| **código gerado** | teste o gerador, uma vez |
| **`__repr__`/`toString` de depuração** | a menos que apareça para o usuário |

**A exceção que confirma a regra:** teste o código de terceiro quando você depende de um
comportamento **específico e sutil** dele. Exemplo real: o teste do projeto-modelo que
verifica que `node:sqlite` devolve inteiros como `number` e não como `string`. Não é teste da
biblioteca; é teste da sua **suposição** sobre ela — e é ela que vai quebrar na atualização.

---

## 6. Como nomear

O nome é a interface do teste. Três padrões que funcionam:

| Padrão | Exemplo |
|---|---|
| `deve_<comportamento>_quando_<condição>` | `deve_recusar_cupom_quando_expirado` |
| `<condição>_<resultado esperado>` | `cupom_expirado_e_recusado` |
| frase de negócio | `cliente_nao_paga_pelo_tempo_pausado` |

Um padrão que **não** funciona:

| Antipadrão | Problema |
|---|---|
| `test_calcular_desconto` | qual caso? há dez. |
| `test_calcular_desconto_2` | pior ainda |
| `test_funciona` | não diz nada |
| `test_bug_1234` | o Jira morre, o teste fica; ponha o número no *docstring*, não no nome |

**Teste do bom nome:** leia só os nomes de um arquivo, em sequência. Se isso não descreve o
que o módulo faz, os nomes estão errados.

```bash
pytest --collect-only -q tests/test_assinatura.py
```

---

## 7. Testes que testam o teste

Um teste que nunca falhou é uma hipótese não verificada. Três formas de verificar:

**1. Veja falhar antes de ver passar.** É a razão nº 1 de o TDD funcionar mesmo para quem
não gosta de TDD. Se você escreveu o teste depois, quebre o código de propósito por um
instante.

**2. Mutação manual.** Mude `>=` para `>`. Troque `MAX_TENTATIVAS = 3` por `4`. Inverta um
`if`. Se nenhum teste ficar vermelho, você tem uma lacuna — e a cobertura não vai te contar.

**3. Meta-teste.** Para espaços enumeráveis, teste se o **teste** está completo:

```python
def test_a_tabela_cobre_todas_as_combinacoes():
    esperado = {(e, a) for e in Estado for a in ACOES}
    coberto = {(i, a) for i, a, _ in TABELA}
    assert coberto == esperado
```

Este é o teste que fica vermelho quando alguém acrescenta um estado novo à enum — sem ele,
o estado novo entraria sem cobertura e **a porcentagem de cobertura não cairia**.

---

## 8. Os cinco porquês: por que mocks demais quebram a refatoração?

**1. Por quê?** Porque o mock verifica **como** o código faz, não **o que** ele produz.

**2. Por que isso é diferente?** Porque `assert servico.gateway.cobrar.called` afirma que
existe um objeto chamado `gateway` com um método chamado `cobrar`, chamado exatamente uma
vez, com aqueles argumentos. Isso é a **estrutura interna**, não o resultado.

**3. Por que a estrutura interna não deveria estar no teste?** Porque refatorar é, por
definição, mudar a estrutura interna preservando o comportamento. Se o teste conhece a
estrutura, todo *refactor* o quebra.

**4. Por que isso é grave, e não só chato?** Porque o time aprende que refatorar "dá
trabalho" — cada limpeza de código vem com 40 testes vermelhos para consertar à mão. O
resultado observável é que **o time para de refatorar**, e a base apodrece. A suíte que
deveria dar coragem passa a dar medo.

**5. Por que então os mocks existem?** Porque para dependências **fora do processo** não há
alternativa: não se pode cobrar de verdade no cartão a cada execução da suíte. Aí o
acoplamento à estrutura é o preço de admissão, e ele é aceitável porque aquela fronteira é
**estável por natureza** — a API do gateway muda raramente, e quando muda, você **quer**
que os testes quebrem.

**Parada legítima: é um trade-off econômico explícito.** Mock em fronteira estável = custo
baixo, benefício alto. Mock em código interno volátil = custo alto, benefício zero. A regra
da seção 2.4 é a aplicação direta disso.

---

## 9. Clássica × mockista: tabela de decisão

| Situação | Use objeto real | Use dublê |
|---|---|---|
| outra função pura sua | ✅ | ❌ |
| outro objeto de domínio seu | ✅ | ❌ |
| repositório em memória (fake) | ✅ | — (o fake **é** o dublê, e é o certo) |
| banco de dados real | só em teste de integração | ✅ nos unitários |
| chamada HTTP externa | ❌ | ✅ |
| relógio, `random`, UUID | ❌ | ✅ (ou injete) |
| envio de e-mail / SMS | ❌ | ✅ (spy, para verificar) |
| fila de mensagens | só em integração | ✅ |
| sistema de arquivos | `tmp_path` é barato → real | opcional |

**Regra de bolso final:** se a dependência é rápida, determinística e sua, **use a de
verdade**. Se ela sai do processo, dublê.

---

## 10. Sinais de que seus testes unitários estão doentes

| Sintoma | Diagnóstico provável | Remédio |
|---|---|---|
| o teste tem mais linhas de setup do que de verificação | o código exige um universo montado | injeção de dependência ([cap. 20](20-testabilidade-e-design.md)) |
| todo *refactor* quebra dezenas de testes | mocks demais, ou testes de estrutura | verificar estado, não interação |
| você precisa ler o código de produção para entender o teste | o teste não documenta nada | renomear, simplificar cenário |
| o teste tem `if`/`for` com lógica | você está reimplementando a função no teste | valores literais |
| a suíte só passa numa ordem | estado compartilhado | isolar; rodar embaralhado |
| ninguém sabe por que aquele teste existe | falta o "porquê" | *docstring* com a regra de negócio |
| o teste passa mesmo com o corpo da função apagado | teste vazio de conteúdo | mutação manual para confirmar |

O último é o mais assustador e mais comum do que parece. Exemplo real, em JavaScript:

```javascript
it('rejeita valor negativo', async () => {
  assert.rejects(async () => validar(-1));   // ← falta o await!
});
```

Sem o `await`, `assert.rejects` devolve uma promessa que ninguém espera. O teste **sempre
passa**, mesmo que `validar(-1)` retorne normalmente.

---

## 11. Teste unitário em código que não foi feito para isso

O caso mais comum do mundo real. Estratégia, em ordem:

1. **Não tente testar tudo.** Escolha o pedaço que você vai mudar.
2. **Escreva um teste de caracterização** ([exemplo 11](06-exemplos.md)) para ter uma rede.
3. **Encontre a "costura"** (*seam*, termo de Michael Feathers): um ponto onde você pode
   mudar o comportamento sem editar o código naquele ponto. Em Python: `monkeypatch`,
   argumento com valor-padrão, atributo de módulo. Em JavaScript: parâmetro com valor
   padrão, `vi.mock`, injeção pelo construtor.
4. **Extraia a lógica pura.** A refatoração de maior retorno em código legado é separar
   "decidir" de "fazer": mova o cálculo para uma função sem I/O e teste essa.
5. **Só então** escreva o teste unitário de verdade.

Detalhamento em [20-testabilidade-e-design.md](20-testabilidade-e-design.md).

---

## Autoteste

1. Por que a definição "teste de uma unidade isolada" é insuficiente?
2. Aplique o teste decisivo do inline a `total = subtotal + frete`. O que ele revela?
3. Em que três situações a escola mockista está certa?
4. Enuncie a regra prática deste curso sobre o que mockar.
5. Cite os três sentidos de "isolado" e diga quais são inegociáveis.
6. Por que "um assert por teste" é uma simplificação ruim? Qual é a formulação correta?
7. Cite quatro coisas que **não** se deve testar, e a exceção que confirma a regra.
8. Descreva as três formas de "testar o teste".
9. Percorra os cinco porquês de "mocks demais quebram a refatoração" até a parada legítima.
10. Você tem um teste com 25 linhas de setup e 2 de asserção. Qual é o diagnóstico?
11. O que é uma "costura" (*seam*) e para que serve?
12. Por que `assert.rejects` sem `await` produz um teste que sempre passa?
