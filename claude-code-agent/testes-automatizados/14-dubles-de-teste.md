# 14 · Dublês de teste — a taxonomia e o que fazer com ela

`Nível: intermediário` · `Última atualização: 12/08/2026`

**Dublê de teste** (*test double*) é o termo guarda-chuva, cunhado por Gerard Meszaros em
*xUnit Test Patterns* (2007), para qualquer objeto falso que substitui uma dependência real
durante um teste. A analogia é o dublê de cinema: parece o ator, faz a cena perigosa, e
ninguém espera que ele saiba atuar.

---

## 1. Por que existem

Três motivos, em ordem de força:

| Motivo | Exemplo |
|---|---|
| a dependência é **cara ou lenta** | banco, rede, API paga |
| a dependência é **não determinística** | relógio, `random`, UUID |
| a dependência é **irreversível ou perigosa** | cobrar cartão, enviar e-mail, apagar dado |

Repare no que **não** está na lista: "para isolar minha classe das outras classes minhas".
Esse é o uso que produz suítes frágeis, e a discussão está em
[13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md).

---

## 2. Os cinco tipos de Meszaros

```
                       ┌──────────────┐
                       │    DUBLÊ     │
                       └──────┬───────┘
        ┌────────────┬────────┼────────┬────────────┐
        │            │        │        │            │
    ┌───▼──┐    ┌────▼──┐ ┌───▼──┐ ┌───▼──┐   ┌─────▼───┐
    │DUMMY │    │ STUB  │ │ SPY  │ │ MOCK │   │  FAKE   │
    └──────┘    └───────┘ └──────┘ └──────┘   └─────────┘
    nunca é     responde  registra  verifica  implementação
    usado       o que     o que     na hora   funcional
                mandaram  aconteceu  se bate   simplificada
```

### 2.1 Dummy — o objeto que só preenche espaço

Nunca é usado. Existe só porque a assinatura exige um argumento.

```python
def test_erro_de_validacao_nem_chega_a_cobrar():
    servico = ServicoRenovacao(
        repositorio=RepositorioMemoria(),
        gateway=None,          # ← dummy: este caminho nunca cobra
        relogio=RelogioFixo(HOJE),
        notificador=None,      # ← dummy
    )
    with pytest.raises(CupomInvalido):
        servico.preco_a_cobrar(assinatura, "INVENTADO")
```

**Quando usar:** raramente. Se você precisa de muitos dummies, a assinatura está grande
demais — é um cheiro de projeto, não de teste.

### 2.2 Stub — responde o que o teste mandou

Devolve valores prontos. **Não se verifica nada nele.**

```python
class RelogioFixo:
    def __init__(self, data): self._data = data
    def hoje(self): return self._data
```

```javascript
const gatewayQueAprova = { cobrar: async () => new Cobranca(true, 'tx-1') };
```

**Quando usar:** sempre que a dependência só **fornece** um valor de entrada para a lógica.
É o dublê mais inofensivo que existe.

### 2.3 Spy — registra o que aconteceu

Deixa a chamada acontecer (ou não) e **guarda o histórico**, que o teste inspeciona depois.

```python
@dataclass
class NotificadorEspiao:
    mensagens: list = field(default_factory=list)

    def avisar(self, cliente, assunto, corpo):
        self.mensagens.append((cliente, assunto, corpo))
```

```python
def test_avisa_o_cliente_do_cancelamento():
    ...
    assert espiao.assuntos_de("ana@ex.br") == ["Assinatura cancelada"]
```

**Quando usar:** quando o efeito colateral **é** o comportamento — enviar e-mail, publicar
evento, gravar log de auditoria. Não há estado a verificar; a chamada é o resultado.

**Vantagem sobre o mock:** a asserção fica **no fim**, junto com as outras, em vez de ser
uma expectativa configurada antes. Testes com spy leem melhor.

### 2.4 Mock — verifica a interação, na hora

A diferença conceitual em relação ao spy: um mock tem **expectativas configuradas antes** e
falha se elas não forem satisfeitas.

```python
def test_gateway_recebe_cliente_e_valor_do_plano():
    gateway = Mock()
    gateway.cobrar.return_value = Cobranca(True, "tx-abc")
    servico = ServicoRenovacao(repo, gateway, RelogioFixo(HOJE), NotificadorEspiao())

    servico.renovar_vencidas()

    gateway.cobrar.assert_called_once_with("ana@ex.br", Dinheiro(1990))
```

> **Nota de vocabulário:** na prática, quase ninguém respeita a distinção estrita
> spy/mock. `unittest.mock.Mock`, `vi.fn()` e `t.mock.fn()` são todos "spies que também
> sabem fazer asserção de interação". A distinção continua útil como **modo de pensar**:
> *"estou verificando estado ou interação?"* é a pergunta que importa.

**Quando usar:** com parcimônia, e só em fronteira externa.

### 2.5 Fake — implementação funcional simplificada

Funciona de verdade, mas com um atalho que a torna imprópria para produção.

```python
class RepositorioMemoria:
    def __init__(self, assinaturas=()):
        self._dados = {a.id: a for a in assinaturas}
    def salvar(self, a): self._dados[a.id] = a
    def buscar(self, id): return self._dados.get(id)
    def listar_vencidas(self, hoje):
        return sorted((a for a in self._dados.values() if a.esta_vencida(hoje)),
                      key=lambda a: a.id)
```

Exemplos clássicos: repositório em memória, SQLite no lugar do Postgres, servidor SMTP que
guarda em lista, sistema de arquivos em memória.

**Quando usar:** é o **melhor dublê** para dependências com estado (banco, cache, fila). Ele
dá testes que verificam estado — logo, resistentes a refatoração — sem pagar o I/O.

**O risco, e o antídoto:** o fake pode mentir. Ele passa e o real quebra. O antídoto é o
**teste de contrato** — a mesma bateria rodando contra o fake e contra o real
([exemplo 10](06-exemplos.md)). Sem ele, o fake é uma hipótese não verificada.

### 2.6 O sexto tipo, que não está na lista de Meszaros

**Sabotador** (ou *stub que explode*): existe para exercitar o caminho de erro.

```python
class GatewayQueExplode:
    def __init__(self, erro=None):
        self.erro = erro or TimeoutError("gateway indisponível")
    def cobrar(self, cliente, valor):
        raise self.erro
```

Não tem nome consagrado, mas é indispensável: **o caminho triste é metade do valor da
suíte**, e sem um sabotador ninguém sabe o que o sistema faz quando o provedor cai.

---

## 3. Tabela de decisão

| Você quer... | Use |
|---|---|
| preencher um argumento que não será usado | **dummy** |
| fornecer um valor de entrada fixo | **stub** |
| verificar que um efeito colateral aconteceu | **spy** |
| verificar argumentos exatos numa fronteira externa | **mock** |
| substituir algo com estado (banco, cache) | **fake** + teste de contrato |
| exercitar o caminho de erro | **sabotador** |
| substituir sua própria função pura | **nada** — use a de verdade |

---

## 4. Estado × interação: a decisão que importa

Toda a taxonomia acima existe para servir a uma escolha:

| | Verificação de **estado** | Verificação de **interação** |
|---|---|---|
| pergunta | "como o mundo ficou?" | "o que foi chamado?" |
| ferramenta | fake, objeto real | mock, spy |
| exemplo | `assert repo.buscar("a1").estado is CANCELADA` | `gateway.cobrar.assert_called_once()` |
| resiste a refatoração | **sim** | **não** |
| detecta o quê | resultado errado | sequência errada |
| quando é a única opção | — | efeito sem rastro (e-mail, log) |

**Regra:** verifique **estado** sempre que possível; **interação** só quando não há estado
para verificar.

Exemplo do projeto-modelo, com as duas formas do mesmo teste:

```python
# ✅ estado — resiste a refatoração
def test_recusa_deixa_inadimplente(self):
    servico, repo, *_ = montar(vencida("a1", "ana@ex.br"),
                               gateway=GatewayFalso(aprovar=False))
    servico.renovar_vencidas()
    assert repo.buscar("a1").estado is Estado.INADIMPLENTE


# ⚠️ interação — quebra se a implementação mudar de `registrar_falha`
#    para um método com outro nome, mesmo com o comportamento idêntico
def test_recusa_chama_registrar_falha(self):
    assinatura = Mock()
    ...
    assinatura.registrar_falha.assert_called_once()
```

O segundo teste tem uma propriedade péssima: ele passaria mesmo que `registrar_falha`
estivesse **quebrada**, porque o objeto é um mock. Ele testa o mock, não o sistema.

---

## 5. A armadilha nº 1: o teste que testa o mock

```python
def test_calcula_o_total(self):
    calculadora = Mock()
    calculadora.somar.return_value = 100

    resultado = calculadora.somar(40, 60)

    assert resultado == 100          # ← testa o Mock, não o seu código
    calculadora.somar.assert_called_with(40, 60)
```

Este teste passa para sempre e não verifica **nada** do sistema. Parece bobo escrito assim,
mas em suíte real ele aparece disfarçado, com quatro camadas de mock entre o teste e a coisa
verificada.

**Sintoma para procurar:** se você apagar o corpo da função de produção e o teste continuar
verde, ele testa o mock.

---

## 6. A armadilha nº 2: mock sem verificação de assinatura

```python
from unittest.mock import Mock

gateway = Mock()
gateway.metodo_que_nunca_existiu()      # não levanta nada. Passa.
gateway.cobrar("ana", 1, 2, 3, 4, 5)    # também passa.
```

`Mock()` responde a **qualquer** atributo com outro `Mock()`. Se o contrato mudar de
`cobrar` para `criar_cobranca`, o mock continua "funcionando", o teste continua verde, e a
produção quebra.

**A correção em Python:**

```python
from unittest.mock import create_autospec

gateway = create_autospec(GatewayHttp, instance=True)
gateway.metodo_que_nunca_existiu()      # AttributeError ✅
gateway.cobrar("ana")                   # TypeError: falta argumento ✅
```

Também servem `Mock(spec=GatewayHttp)` e `@patch(..., autospec=True)`.

**Em JavaScript não existe equivalente.** `vi.fn()` e `t.mock.fn()` não conhecem assinatura
nenhuma. As mitigações reais são três:

1. **TypeScript** (ou JSDoc com `checkJs`), que verifica o formato em tempo de compilação;
2. **teste de contrato**, que roda a mesma bateria em toda implementação;
3. **preferir fakes a mocks** — um fake que implementa a interface errada quebra na hora.

Esse é um ponto em que o ecossistema Python está objetivamente à frente.

---

## 7. A armadilha nº 3: onde apontar o `patch`

O erro nº 1 de `unittest.mock`. A regra:

> **Substitua o nome onde ele é *usado*, não onde é *definido*.**

```python
# clima.py
import urllib.request

def temperatura():
    return urllib.request.urlopen(...)    # usa o módulo → alvo: "clima.urllib.request.urlopen"
```

```python
# tempo.py
from urllib.request import urlopen        # importou o NOME para dentro do módulo

def temperatura():
    return urlopen(...)                   # alvo: "tempo.urlopen"
```

Se você apontar para `"urllib.request.urlopen"` no segundo caso, o `patch` funciona — e
**não faz efeito nenhum**, porque `tempo.urlopen` já é uma referência ao objeto original,
capturada no momento do `import`.

**Sintoma:** o teste tenta acessar a rede de verdade, ou o mock nunca é chamado.

Em JavaScript o problema equivalente é o **içamento** (*hoisting*) do `vi.mock`, que é movido
para antes dos `import` pelo transformador — daí a existência de `vi.hoisted()`.

---

## 8. Quantos dublês são demais?

Um heurístico útil, de Khorikov: **conte os dublês por teste.**

| Dublês no teste | Diagnóstico |
|---|---|
| 0 | ótimo — função pura ou objetos reais |
| 1–2 | normal — as fronteiras externas do caso de uso |
| 3–4 | atenção — o objeto tem colaboradores demais? |
| 5+ | o problema é o **projeto**, não o teste |

Cinco dublês significa que a unidade sob teste depende de cinco coisas. Nenhuma técnica de
teste conserta isso; a correção é no código — extrair, agrupar, inverter dependência. Ver
[20-testabilidade-e-design.md](20-testabilidade-e-design.md).

---

## 9. Os cinco porquês: por que um fake é melhor que um mock para o repositório?

**1. Por quê?** Porque com o fake você verifica **estado** (`repo.buscar("a1").estado`), e
com o mock você verifica **chamadas** (`repo.salvar.assert_called_with(...)`).

**2. Por que verificar estado é melhor?** Porque estado é o que o usuário percebe. Se a
assinatura ficou cancelada, ela está cancelada — não importa se foi salva com um `salvar()`
ou dois.

**3. Por que "um `salvar()` ou dois" importaria com mock?** Porque
`assert_called_once_with(...)` afirma **exatamente uma** chamada. Uma refatoração que salve
duas vezes (idempotente, mesmo resultado) quebra o teste sem quebrar o sistema.

**4. Por que isso não acontece com o fake?** Porque o fake **é** um repositório: salvar duas
vezes tem o mesmo efeito final que salvar uma. O teste observa o mundo, não a coreografia.

**5. Então por que alguém usa mock para repositório?** Por duas razões, uma boa e uma ruim.
A boa: quando não existe fake e escrevê-lo custaria caro (uma API externa complexa). A
ruim: porque é o que a ferramenta oferece na primeira página da documentação, e escrever um
fake exige pensar no contrato.

**Parada legítima: é um trade-off de custo de construção.** Um fake custa de 20 a 100 linhas
a mais; ele se paga a partir de mais ou menos cinco testes que o usam, e se paga muitas
vezes na primeira refatoração grande. Abaixo disso, mock é aceitável.

---

## 10. Onde os dublês devem morar no código

Decisão frequentemente esquecida: o `GatewayFalso` fica no pacote de produção ou no de
testes?

| Opção | Vantagem | Desvantagem |
|---|---|---|
| junto do contrato (**produção**) | quem consome sua biblioteca pode testar o próprio código | algumas dezenas de linhas no pacote publicado |
| na pasta de testes | pacote limpo | cada consumidor reinventa o fake, e cada um erra diferente |

**Recomendação:** se você publica uma biblioteca, **entregue o fake junto**. É o que fazem
bibliotecas maduras, e é o que o projeto-modelo faz — com o motivo escrito no código.

---

## 11. Resumo em uma frase

> Use **objetos reais** para o seu domínio, **fakes verificados por contrato** para
> dependências com estado, **stubs** para entradas, **spies** para efeitos sem rastro,
> **sabotadores** para o caminho triste, e **mocks** apenas na fronteira externa — sempre com
> verificação de assinatura, quando a linguagem permitir.

---

## Autoteste

1. Quais são os três motivos legítimos para usar um dublê? Qual motivo comum **não** está na lista?
2. Diferencie stub, spy e mock em uma frase cada.
3. Por que o fake é o melhor dublê para dependências com estado, e qual é o risco dele?
4. O que é um sabotador e por que ele é indispensável, apesar de não estar na taxonomia clássica?
5. Enuncie a regra sobre verificação de estado × interação.
6. Como descobrir se um teste está testando o mock em vez do sistema?
7. Por que `Mock()` sem `spec` é perigoso? Qual é a correção em Python, e por que ela não existe em JavaScript?
8. `tempo.py` faz `from urllib.request import urlopen`. Qual é o alvo do `patch`, e qual é o sintoma de errar?
9. Seu teste tem 6 dublês. O que isso indica, e onde está a correção?
10. Percorra os cinco porquês de "fake é melhor que mock para repositório" até a parada legítima.
11. Você publica uma biblioteca. Onde o fake deve morar, e por quê?
