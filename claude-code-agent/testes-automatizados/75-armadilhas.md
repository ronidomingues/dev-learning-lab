# 75 · Armadilhas, mitos e más práticas

`Nível: intermediário` · `Última atualização: 13/08/2026`

Cada item traz: **o que é**, **por que persiste**, e **o que fazer**. A segunda parte importa
tanto quanto a terceira: prática ruim que sobrevive tem uma razão, e atacar a razão funciona
melhor que repetir a regra.

---

## Parte I — Mitos

### M1. "Cobertura de 100 % significa que está bem testado"

**Por que persiste:** é um número, cabe num painel, e sobe quando o time trabalha. Métrica
visível vence métrica útil.

**Por que é falso:** cobertura mede execução, não verificação. Um teste sem asserção cobre
100 %. E cobertura **não pode** acusar código ausente — o tratamento de lista vazia que você
esqueceu não tem linha para cobrir.

**O que fazer:** use cobertura como detector de lacunas (`term-missing`), não como meta. Meça
a força da suíte com análise de mutação no núcleo. Ver
[19-cobertura-e-metricas.md](19-cobertura-e-metricas.md).

---

### M2. "Testes garantem que não há bugs"

**Por que persiste:** é o que se quer que seja verdade, e é o que se vende para o gestor.

**Por que é falso:** Dijkstra, 1970 — testes mostram a presença de defeitos, nunca a
ausência. Testar é amostrar um espaço astronomicamente grande.

**O que fazer:** prometa o que a suíte entrega: **detecção de regressão** e **coragem para
mudar**. Quem promete ausência de bugs perde credibilidade no primeiro incidente.

---

### M3. "TDD é comprovadamente melhor"

**Por que persiste:** foi promovido com fervor por figuras influentes nos anos 2000, e para
quem pratica funciona mesmo.

**Por que é falso como afirmação empírica:** os estudos são inconclusivos, e replicações
sugerem que o ganho vem de **ter testes** e de **trabalhar em passos pequenos e uniformes**,
não da ordem em que se escreve.

**O que fazer:** apresente TDD como disciplina com bom retorno, não como resultado
científico. E meça no seu contexto. Ver [15-tdd.md](15-tdd.md) §6.

---

### M4. "Escrever testes dobra o tempo"

**Por que persiste:** o custo de escrever é visível; o custo de **não** escrever está diluído
em depuração, retrabalho e medo de mexer.

**Por que é enganoso:** o tempo que some é o de abrir o sistema, clicar em cinco telas e
digitar dados de teste manualmente — a cada mudança. Ninguém contabiliza isso.

**O que fazer:** meça o ciclo completo, não só o de escrever. E aceite que **no começo é
mais lento mesmo** — negar isso destrói a credibilidade do argumento.

---

### M5. "Não dá para testar este código"

**Por que persiste:** é literalmente verdade para o código como está.

**Por que é enganoso:** a frase completa é *"não dá para testar este código **sem
modificá-lo**"* — e a modificação necessária é quase sempre uma melhoria.

**O que fazer:** [capítulo 20](20-testabilidade-e-design.md). Comece por caracterização e
extração da lógica pura.

---

### M6. "QA testa, desenvolvedor programa"

**Por que persiste:** é a estrutura organizacional herdada dos anos 1980, e mexer nela é
política, não técnica.

**Por que é enganoso:** o custo de ida e volta entre equipes domina. E ninguém conhece os
caminhos internos de uma função melhor que quem a escreveu.

**O que fazer:** desenvolvedor escreve unitário e integração; especialista de qualidade faz
estratégia, exploratório, E2E e carga — que exigem outra habilidade e são valiosos.

---

## Parte II — Armadilhas técnicas

### A1. Teste que testa o mock

```python
def test_calcula_total():
    calculadora = Mock()
    calculadora.somar.return_value = 100
    assert calculadora.somar(40, 60) == 100     # testa o Mock
```

**Por que persiste:** aparece disfarçado, com quatro camadas de mock entre o teste e a coisa
verificada. Ninguém escreve assim de propósito.

**Como detectar:** apague o corpo da função de produção. Se o teste continua verde, ele testa
o mock.

---

### A2. Teste acoplado à implementação

```python
def test_usa_cache_interno():
    assert servico._cache is not None      # detalhe privado
```

**Por que persiste:** é mais fácil verificar o interno do que pensar no que é observável.

**Consequência:** todo *refactor* quebra dezenas de testes. O time aprende que refatorar dói,
para de refatorar, e a base apodrece.

**Como detectar:** mude a implementação sem mudar o comportamento. Os testes que quebrarem
estão errados.

---

### A3. *Assertion roulette*

```python
def test_assinatura():
    assert a.estado is ATIVA
    assert a.pausar() is None
    assert a.estado is PAUSADA
    assert a.cancelar() is None
    assert a.estado is CANCELADA
```

**Por que persiste:** parece econômico — um setup, cinco verificações.

**Consequência:** a primeira asserção que falha **interrompe** o teste; você descobre os
problemas um por vez, numa série de execuções. E o nome não diz qual comportamento quebrou.

**O que fazer:** um comportamento por teste. Várias asserções sobre o **mesmo** comportamento
são aceitáveis.

---

### A4. Lógica dentro do teste

```python
def test_descontos():
    for valor in [100, 200, 300]:
        esperado = valor * 0.9 if valor > 150 else valor
        assert desconto(valor) == esperado      # reimplementou a função
```

**Por que persiste:** evita repetição, e repetição parece ruim.

**Consequência:** o teste tem o mesmo bug do código. Um `if` no teste é um caminho não
testado do teste.

**O que fazer:** valores literais, calculados por fora. Repetição em teste é aceitável e
frequentemente desejável — **o teste deve ser óbvio, não elegante**.

---

### A5. Testes que dependem uns dos outros

```python
def test_1_cria(): global PEDIDO; PEDIDO = criar()
def test_2_paga(): pagar(PEDIDO)          # depende do test_1 ter rodado
```

**Por que persiste:** economiza setup e o cenário é sequencial mesmo.

**Consequência:** impossível rodar um só, impossível paralelizar, cascata de falhas.

**Como detectar:** `pytest -p randomly` ou `vitest --sequence.shuffle`.

---

### A6. `sleep` para sincronizar

```javascript
await page.click('#salvar');
await new Promise((r) => setTimeout(r, 2000));    // ❌
await expect(page.getByText('Salvo')).toBeVisible();
```

**Por que persiste:** funciona na sua máquina, hoje, e o teste fica verde na hora.

**Consequência:** lento quando não precisa e insuficiente quando a máquina está carregada.
É a causa nº 1 de teste instável.

**O que fazer:** espere por **condição**, nunca por tempo. Playwright, Cypress e Testing
Library têm auto-espera. Para banco e serviço, `healthcheck`.

---

### A7. Fixture-cascata

```python
@pytest.fixture
def cliente(banco, config, cache, fila, relogio, notificador, gateway): ...
```

**Por que persiste:** cada fixture nova parece uma melhoria local.

**Consequência:** ninguém sabe o que um teste está usando. Uma mudança na fixture da raiz
quebra 200 testes em três arquivos.

**O que fazer:** funções de fábrica explícitas para o cenário; fixture só para recurso que
precisa de teardown. E `conftest.py` só para o que é usado por dois ou mais arquivos.

---

### A8. Snapshot podre

**Por que persiste:** `-u` regenera tudo em um segundo, e a revisão de um diff de 400 linhas
é impossível.

**Sinais:** snapshot maior que uma tela; snapshot com data, UUID ou ordem instável dentro;
mudança de uma linha de código altera 30 snapshots.

**O que fazer:** snapshot só para saída pequena, estável, e que você consegue **ler e julgar
em 10 segundos**. Para regra de negócio, asserção explícita.

---

### A9. Teste lento aceito como normal

**Por que persiste:** cada teste lento é só "mais um". A degradação é imperceptível por
semana e brutal por ano.

**Consequência:** a suíte cruza o limiar em que ninguém a roda, e o valor vai a zero.

**O que fazer:** monitore o tempo como se fosse um requisito. `pytest --durations=10` num
relatório periódico. Trate um teste unitário acima de 100 ms como defeito.

---

### A10. Instabilidade normalizada

**Por que persiste:** consertar dá trabalho, rerodar custa um clique.

**Consequência:** **a pior de todas.** Quando o vermelho deixa de significar problema, a
suíte perde a única propriedade que a torna útil. E a partir daí ela tem valor **negativo**:
custa manutenção e não dá sinal.

**O que fazer:** meça a taxa; quarentena **com prazo**; conserte a causa. E trate um teste
instável com a mesma prioridade de um bug em produção — porque é o que ele é, para a suíte.

---

### A11. Mocar o que você não possui

```python
with patch("requests.get") as fake:
    fake.return_value.json.return_value = {"status": "ok"}
```

**Por que persiste:** é a primeira coisa que aparece na documentação.

**Consequência:** você testa a sua **crença** sobre a API alheia. Quando ela muda o formato,
todos os testes continuam verdes e a produção quebra.

**O que fazer:** envolva a API numa camada sua (*anti-corruption layer*), mocke a **sua**
camada, e mantenha **um** teste de integração real (ou VCR) contra a API verdadeira.

---

### A12. Teste que só existe para subir cobertura

```python
def test_repr():
    assert repr(Dinheiro(100))          # sem asserção real
```

**Por que persiste:** a meta de cobertura é do time, e este teste leva 30 segundos para
escrever.

**Consequência:** passivo puro — código a manter, zero proteção, e o número engana quem olha.

**O que fazer:** ataque a causa: tire a meta global de cobertura, ou troque por cobertura do
diff.

---

### A13. Setup gigante

**Por que persiste:** é o código de produção que exige, e o teste só obedece.

**Consequência:** ninguém entende o teste; ninguém escreve testes novos naquele módulo.

**O que fazer:** o setup grande é um **sintoma**. Trate o código, não o teste
([cap. 20](20-testabilidade-e-design.md)).

---

### A14. `assert` sem `await` (JavaScript)

```javascript
it('rejeita', async () => {
  assert.rejects(async () => f());       // ❌ sem await: passa sempre
});
```

**Por que persiste:** o teste fica verde, e verde parece certo.

**Como detectar:** quebre a função de propósito. Se continuar verde, falta `await`.

**Proteção:** `@typescript-eslint/no-floating-promises`, `eslint-plugin-vitest`, e `t.plan(n)`
no `node:test`.

---

### A15. Dados de produção no ambiente de teste

**Por que persiste:** é realista e evita escrever fábricas.

**Consequência:** violação de proteção de dados pessoais (LGPD), dump que envelhece, e testes
que dependem de um registro específico que ninguém sabe por que existe.

**O que fazer:** fábricas no código. Se precisar de realismo, dados **sintetizados** a partir
da distribuição, não os dados reais.

---

### A16. Código que sabe que está em teste

```python
if os.environ.get("AMBIENTE") == "teste":
    return {"aprovada": True}
```

**Por que persiste:** resolve o problema imediato em duas linhas.

**Consequência:** o caminho de produção nunca é exercitado; um erro de configuração vira
incidente; e é uma porta de fraude.

**O que fazer:** injeção. Sempre. Ver [cap. 20](20-testabilidade-e-design.md) §7.

---

## Parte III — Erros de organização

### O1. "Vamos fazer um mutirão de testes"

Projeto separado de "adicionar testes" quase sempre fracassa: produz testes de baixo valor
nas partes fáceis, e para quando a prioridade muda.

**Alternativa:** regra do escoteiro. Todo bug ganha teste; todo arquivo tocado ganha teste.
Em seis meses o código que mais muda — que é o que mais quebra — está coberto.

### O2. Meta de cobertura imposta de cima

Produz exatamente o que a lei de Goodhart prevê. Ver
[19-cobertura-e-metricas.md](19-cobertura-e-metricas.md) §6.

**Alternativa:** cobertura do diff, com limite baixo, como alarme.

### O3. Suíte que ninguém mantém

Testes são código. Sem revisão, sem refatoração e sem exclusão do que ficou redundante, a
suíte apodrece como qualquer outro código.

**Alternativa:** revise testes no PR com o mesmo rigor do código. E **apague** testes
redundantes — isso é permitido e saudável.

### O4. Testar a interface porque a lógica está nela

Se a única forma de testar uma regra é pela tela, a regra está no lugar errado. É um problema
de arquitetura disfarçado de problema de teste.

---

## Tabela de diagnóstico rápido

| Sintoma | Provável causa | Ver |
|---|---|---|
| todo *refactor* quebra testes | acoplamento à implementação | A2, [13](13-teste-unitario-a-fundo.md) |
| a suíte é vermelha "às vezes" | instabilidade | A6, A10 |
| ninguém roda a suíte | lenta demais | A9 |
| bugs escapam com cobertura alta | testes sem força | M1, A12, [19](19-cobertura-e-metricas.md) |
| ninguém escreve testes novos | setup insuportável | A13, [20](20-testabilidade-e-design.md) |
| o teste passa com o código apagado | testa o mock, ou falta `await` | A1, A14 |
| falha só quando roda tudo junto | estado compartilhado | A5 |
| falha só no CI | ambiente, ordem, paralelismo | [21](21-ci-e-automacao.md) §6 |
| a produção quebra e a suíte estava verde | mock do que você não possui | A11 |

---

## Autoteste

1. Por que "100 % de cobertura" é um mito, e o que a métrica realmente mede?
2. O que a evidência empírica diz sobre TDD, e como apresentar isso honestamente?
3. Como detectar, em 30 segundos, que um teste está testando o mock?
4. Por que um `if` dentro de um teste é um problema?
5. Por que repetição em teste é aceitável, ao contrário de em código de produção?
6. Qual é a armadilha "pior de todas", e por que ela dá valor **negativo** à suíte?
7. Explique por que mocar `requests.get` é diferente de mocar a sua própria camada.
8. Cite três sinais de snapshot podre.
9. Por que um "mutirão de testes" costuma fracassar, e qual é a alternativa?
10. Você tem 100 % de cobertura e bugs escapando. Quais três hipóteses investigar?
11. Por que dados de produção em ambiente de teste é um problema jurídico **e** técnico?
12. Um teste passa com o corpo da função apagado. Quais são as duas causas prováveis?
