# 17 · Verificação — o gargalo, e como alargá-lo

**Nível:** intermediário → avançado · **Escrito em:** 20/08/2026

> Este é o arquivo mais importante do curso. Se você ler só um, leia este.

---

## 1 · A pirâmide de verificação

Nem toda verificação custa igual nem pega a mesma coisa. Ordene por
**custo por execução**:

```
                    ┌─────────────────────┐
   caro, lento,     │  JULGAMENTO HUMANO  │  o que só você julga
   não escala       │  arquitetura, UX,   │
                    │  negócio, ética     │
                    ├─────────────────────┤
                    │  TESTE E2E          │  fluxo real, poucos
                    ├─────────────────────┤
                    │  TESTE INTEGRAÇÃO   │  banco, HTTP, fila
                    ├─────────────────────┤
                    │  TESTE UNITÁRIO     │  lógica, muitos
                    ├─────────────────────┤
                    │  TIPOS              │  contrato, grátis
                    ├─────────────────────┤
   barato, rápido,  │  LINTER / FORMATTER │  padrão, grátis
   escala infinito  │  COMPILADOR         │  sintaxe, grátis
                    └─────────────────────┘
```

**A estratégia é uma frase:** empurre cada verificação para o nível mais baixo
possível. Tudo que uma camada de baixo pega, as de cima não precisam pegar — e
as de baixo rodam mil vezes por dia de graça.

Corolário direto: **cada coisa que você aprende a verificar automaticamente é
capacidade de delegação que você ganha para sempre.**

---

## 2 · Por que a camada de tipos ficou mais valiosa

Antes: tipos evitavam erro de digitação e ajudavam o editor.
Agora: **tipos são um revisor gratuito de código que você não escreveu.**

Quando o agente inventa um campo, troca a ordem dos argumentos, ou devolve
`Pedido` onde se esperava `PedidoSalvo`, o verificador de tipos pega **antes de
qualquer teste rodar**, em milissegundos, sem você olhar.

### Tipos que trabalham a seu favor

| Em vez de | Use | O que passa a ser impossível |
|---|---|---|
| `str` para tudo | `NewType("CPF", str)` / *branded types* | Passar e-mail onde se espera CPF |
| `int` para dinheiro | `Decimal` ou centavos em `int` com tipo próprio | Erro de arredondamento silencioso |
| `dict` solto | `dataclass` / `TypedDict` / `interface` | Campo inventado |
| `Optional` em tudo | Tornar não-nulo o caso comum | Verificação de nulo esquecida |
| `any` / `object` | Tipo real | Tudo. `any` desliga a camada inteira |

```python
from typing import NewType
from decimal import Decimal

CPF = NewType("CPF", str)
Centavos = NewType("Centavos", int)

def cobrar(cpf: CPF, valor: Centavos) -> None: ...

# cobrar("joao@exemplo.com", 1000)  ← o verificador reprova
```

> **Regra do portão:** proíba `any`, `# type: ignore`, `@ts-ignore` em código
> gerado. É a forma nº 1 de o agente "resolver" um erro de tipo sem resolver
> nada. Verificação mecânica no [projeto-modelo](07-projeto-modelo/README.md).

---

## 3 · Testes na era dos agentes: o que muda

### Muda 1 — velocidade virou requisito, não conforto

Antes, suíte lenta era irritante. Agora ela **muda o comportamento do agente**.

| Tempo da suíte | O que o agente faz |
|---|---|
| < 10 s | Roda a cada mudança. Converge rápido |
| 10 s – 2 min | Roda a cada duas ou três mudanças |
| 2 – 10 min | Roda no fim. Erros se acumulam antes de aparecer |
| > 10 min | Praticamente não roda. **Ele passa a adivinhar** |

Lembre da matemática do [15](15-o-loop-do-agente.md): verificação intermediária
é o que impede a probabilidade de degradar como `p^n`. Suíte lenta remove a
verificação intermediária. **Portanto, acelerar a suíte não é otimização —
é o que torna a delegação viável.**

Alvo prático: **testes unitários em menos de 30 segundos**, com um comando que
roda só o subconjunto relevante.

### Muda 2 — o teste virou a especificação executável

O agente lê os testes para entender o que o código deve fazer. Um teste bem
nomeado ensina mais que um parágrafo de documentação — e nunca fica obsoleto
sem alguém notar.

```python
# ruim: ensina nada
def test_calculo(): ...

# bom: o nome É a especificação
def test_frete_gratis_acima_de_200_reais_exceto_para_regiao_norte(): ...
```

### Muda 3 — testes gerados por IA falham de um jeito específico

Os quatro padrões, em ordem de frequência:

**a) Asserção vazia**
```python
resultado = calcular(10)
assert resultado is not None      # passa sempre; prova nada
```

**b) Teste tautológico** — testa a implementação, não o requisito
```python
def test_desconto():
    esperado = preco * 0.9        # a mesma fórmula do código
    assert aplicar_desconto(preco) == esperado
```
Se a fórmula do código estiver errada, o teste está igualmente errado. Este é o
padrão mais perigoso porque **parece um teste completo**.

**c) Mock que engole o comportamento sob teste**
```python
@patch("modulo.salvar_pedido")
def test_processa(mock_salvar):
    mock_salvar.return_value = {}
    assert processar(pedido) is not None   # nada real foi exercido
```

**d) Só caminho feliz** — nenhuma entrada inválida, nenhum limite, nenhum erro.

### A regra que resolve os quatro

> **Todo teste deve falhar se você quebrar o código de propósito.**

Isso não é filosofia; é um procedimento que se executa. Chama-se **teste de
mutação**.

---

## 4 · Teste de mutação — a verificação da verificação

Cobertura mede **execução**. Mutação mede **detecção**. São coisas diferentes, e
só a segunda importa.

```
código original ──► suíte ──► verde
código mutado   ──► suíte ──► DEVE ficar vermelho
                              se ficar verde, a mutação "sobreviveu"
                              → o teste não testa aquilo
```

### Mutações que valem

| Mutação | Pega o quê |
|---|---|
| `>` → `>=` | Erro de limite, off-by-one |
| `+` → `-` | Fórmula |
| `and` → `or` | Lógica de condição |
| `True` → `False` | Ramo não exercido |
| remover uma linha | Linha morta ou não verificada |
| constante `N` → `N+1` | Valor mágico não checado |

### Ferramentas

| Linguagem | Ferramenta |
|---|---|
| Python | `mutmut`, `cosmic-ray` |
| JS/TS | `Stryker` |
| Java | `PIT` |
| Go | `go-mutesting` |
| Qualquer | o script de 30 linhas do [exemplo 3](06-exemplos.md) |

### Como usar sem virar tortura

Mutação é cara: roda a suíte inteira uma vez por mutação. Não rode em tudo.

**Estratégia recomendada:**
- Rode **só nos módulos críticos** (dinheiro, autenticação, permissão).
- Rode **semanalmente**, não a cada PR.
- Rode **quando os testes foram gerados por IA** — é aí que o retorno é maior.

---

## 5 · Verificações que quase ninguém usa e deveriam

### Teste de propriedade (*property-based testing*)

Em vez de casos específicos, você declara uma **propriedade** e a ferramenta
gera centenas de entradas tentando quebrá-la.

```python
from hypothesis import given, strategies as st

@given(st.decimals(min_value=0, max_value=10**6, places=2))
def test_arredondamento_nunca_perde_centavo(valor):
    partes = dividir_em_parcelas(valor, 3)
    assert sum(partes) == valor        # invariante
```

**Por que combina especialmente bem com IA:** o modelo é bom em caminho feliz e
ruim em caso de borda. Teste de propriedade **é** uma máquina de gerar casos de
borda. Ele cobre exatamente o ponto cego.

Ferramentas: `hypothesis` (Python), `fast-check` (JS), `jqwik` (Java),
`proptest` (Rust).

### Teste de arquitetura

Verifica que as fronteiras são respeitadas — algo que o agente viola com
naturalidade, porque ele não "vê" a arquitetura, só arquivos.

```python
# com import-linter (Python)
# .importlinter
[importlinter:contract:dominio-puro]
name = Domínio não depende de infraestrutura
type = forbidden
source_modules = app.dominio
forbidden_modules = app.adapters, app.web, sqlalchemy, requests
```

Equivalentes: ArchUnit (Java), `dependency-cruiser` (JS), `go-arch-lint` (Go).

### Teste de caracterização

Trava o comportamento atual antes de mexer. Ver [exemplo 10](06-exemplos.md).
Indispensável em qualquer migração conduzida por agente.

### Teste de contrato

Garante que produtor e consumidor de uma API concordam. Pact, Spring Cloud
Contract, ou simplesmente um esquema JSON versionado e testado dos dois lados.

---

## 6 · O portão

Toda verificação automática precisa de um lugar onde **decide**. Isso é o
portão.

```
        agente
          │
          ▼
    ┌───────────┐
    │  PORTÃO   │  formatador · linter · tipos · testes · segredos ·
    │           │  dependências · escopo · tamanho · cobertura do diff
    └─────┬─────┘
          │ aprovado
          ▼
      revisão humana ─── só o que a máquina não julga
          │
          ▼
        main
```

### Regras de projeto de portão

| Regra | Por quê |
|---|---|
| **Rápido** (< 5 min) | Portão lento é contornado |
| **Determinístico** | Se falha aleatoriamente, ninguém confia; e sem confiança ele é desligado |
| **Mensagem acionável** | "Reprovado" não ajuda; "reprovado: `CA-03` sem teste" ajuda |
| **Duas severidades** | Bloquear tudo gera fadiga de alerta e desativação |
| **Sem IA dentro** | Portão não pode ser não-determinístico. Ver [projeto-modelo](07-projeto-modelo/README.md) |

### Ordem correta das etapas

Da mais rápida para a mais lenta, **falhando cedo**:

```
1. formatador   (segundos)
2. linter       (segundos)
3. tipos        (segundos a 1 min)
4. segredos     (segundos)
5. escopo/tamanho do diff (instantâneo)
6. testes unitários (< 1 min)
7. testes de integração (minutos)
8. E2E          (minutos)
```

Rodar E2E antes do linter é desperdiçar cinco minutos para descobrir um espaço
sobrando.

---

## 7 · Cobertura do *diff*: a métrica certa

Cobertura total do projeto é uma métrica ruim: sobe devagar, ninguém age sobre
ela, e um número alto convive com testes tautológicos.

**Cobertura do diff** é outra coisa: *das linhas que esta mudança adiciona,
quantas são exercidas por algum teste?*

| Métrica | Utilidade |
|---|---|
| Cobertura total = 78% | Quase nenhuma. Não diz nada sobre o risco de hoje |
| Cobertura do diff = 34% | **Alta.** Duas em cada três linhas novas entram sem nenhuma verificação |

Ferramentas: `diff-cover` (Python), `nyc` com filtro por diff (JS),
Codecov/Coveralls com relatório por PR.

**Sugestão de política, e é opinião:** exija ≥ 80% de cobertura do diff em
código gerado por agente, e permita exceção documentada. Não exija número de
cobertura total — ele cria incentivo para teste decorativo, que é justamente o
que já sobra.

---

## 8 · O que continua sendo humano

Nenhuma automação cobre isto. É onde a sua atenção deve sobrar:

| Julgamento | Por que a máquina não pega |
|---|---|
| **Isto resolve o problema certo?** | Não conhece o problema, só a especificação |
| **A abstração está no nível certo?** | Julgamento estético e de evolução futura |
| **Isso vai ser mantível em dois anos?** | Exige prever mudanças que ainda não existem |
| **Isso duplica algo que já temos?** | O agente não conhece o sistema todo — e a duplicação subiu 81% desde 2023 |
| **O risco vale o benefício?** | Decisão de negócio |
| **Isso é seguro no contexto do nosso negócio?** | Modelo de ameaça é específico |
| **Alguém consegue depurar isto às 3 da manhã?** | Empatia operacional |

> **A tese final:** o portão não substitui a revisão humana — ele **remove da
> revisão humana tudo que uma máquina consegue conferir**, para que a atenção
> escassa sobre no que só um humano julga. Quem monta bem o portão não revisa
> menos; revisa **melhor**.

---

## Autoteste

1. Desenhe a pirâmide de verificação e enuncie a estratégia em uma frase.
2. Por que tipos ficaram mais valiosos com IA do que eram antes?
3. Por que `any` e `# type: ignore` devem ser proibidos no portão?
4. Como o tempo da suíte muda o comportamento do agente? Ligue isso à matemática
   do laço.
5. Cite os quatro padrões de teste ruim gerado por IA. Qual é o mais perigoso e
   por quê?
6. Qual é a regra única que resolve os quatro? Como ela se executa na prática?
7. Qual é a diferença entre cobertura e mutação? Qual das duas importa?
8. Por que teste de propriedade combina especialmente bem com código de IA?
9. Cite cinco regras de projeto de um bom portão e a ordem correta das etapas.
10. Por que cobertura do diff é melhor métrica que cobertura total?
11. Cite quatro julgamentos que continuam humanos e por que a máquina não os pega.

---

**Anterior:** [16-especificacao-e-plano](16-especificacao-e-plano.md) ·
**Próximo:** [18-revisao-de-codigo-gerado](18-revisao-de-codigo-gerado.md)
