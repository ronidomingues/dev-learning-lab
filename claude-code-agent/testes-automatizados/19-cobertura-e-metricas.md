# 19 · Cobertura e métricas — o que medir e no que não acreditar

`Nível: intermediário → avançado` · `Experimentos executados em 13/08/2026`

---

## 1. O que cobertura mede, exatamente

**Cobertura de código** é a fração do código que foi **executada** durante os testes. Só
isso. Ela **não** mede se o teste verificou alguma coisa.

Prova em três linhas:

```python
def test_cobertura_perfeita_sem_verificar_nada():
    aplicar_desconto(10000, 10)     # executou. 100% de cobertura. Zero asserção.
```

Este teste cobre 100 % da função e **passa mesmo que ela devolva o valor errado**. Cobertura
alta é condição **necessária** e não suficiente.

---

## 2. Os quatro critérios, do mais fraco ao mais forte

```python
def classificar(idade, tem_convenio):
    if idade >= 60 and tem_convenio:
        return "prioritario"
    return "normal"
```

### 2.1 Cobertura de linha (*statement*)

Fração de linhas executadas. **Um** teste — `classificar(70, True)` — cobre 100 % das linhas
do `if`? Não: a linha do `return "normal"` fica de fora. Com dois testes, 100 %.

### 2.2 Cobertura de ramo (*branch*)

Cada decisão precisa ser tomada nos dois sentidos. `if` verdadeiro **e** falso.

| Teste | Linha | Ramo |
|---|---|---|
| `(70, True)` | 2/3 | 1/2 |
| `+ (30, False)` | 3/3 ✅ | 2/2 ✅ |

### 2.3 Cobertura de condição / MC-DC

O `if` acima tem **duas** condições ligadas por `and`. Com os dois testes acima, você nunca
exercitou `idade >= 60 and not tem_convenio`. Se alguém trocar `and` por `or`, a cobertura de
ramo continua 100 % **e o bug passa**.

- **cobertura de condição**: cada condição atômica assume verdadeiro e falso.
- **MC-DC** (*Modified Condition/Decision Coverage*): cada condição precisa demonstrar,
  isoladamente, que afeta o resultado. É exigido pela norma **DO-178C** para software
  aeronáutico de nível A — o que dá a medida de quão sério é o critério.

### 2.4 Cobertura de caminho

Todos os caminhos possíveis pelo grafo de fluxo. Cresce **exponencialmente**; um laço torna
o número infinito. Inviável na prática, e é por isso que ninguém a usa.

### 2.5 Resumo

| Critério | Força | Custo | Recomendação |
|---|---|---|---|
| linha | fraca | baixo | insuficiente sozinha |
| **ramo** | média | baixo | **o padrão que você deve ligar** |
| condição / MC-DC | alta | alto | software crítico, ou o núcleo do seu domínio |
| caminho | máxima | inviável | não |

**Ação concreta:** ligue cobertura de ramo hoje.

```toml
# Python — sem isto, você está medindo o critério mais fraco
[tool.coverage.run]
branch = true
```

```bash
node --test --experimental-test-coverage    # já reporta ramo
vitest run --coverage                       # idem
```

---

## 3. O que a cobertura não vê

Três lacunas, do menos para o mais grave.

### 3.1 Falta de asserção

Já visto na seção 1: executar ≠ verificar.

### 3.2 O caso que não existe

Cobertura mede o código que **existe**. Se você esqueceu de tratar a lista vazia, não há
linha para cobrir — e a cobertura fica 100 %.

```python
def primeiro(itens):
    return itens[0]          # e se a lista for vazia? IndexError em produção.
```

Um teste com `[1, 2, 3]` dá 100 % de cobertura de linha, ramo e condição. **A cobertura não
tem como acusar código ausente.** Este é o limite conceitual mais importante da métrica.

### 3.3 O modelo RIP

Para uma falha ser observada é preciso que o defeito seja **executado** (*Reachability*),
que ele **corrompa o estado** (*Infection*) e que a corrupção **chegue à saída**
(*Propagation*). Cobertura compra só a primeira das três.

---

## 4. Análise de mutação — a métrica que mede a suíte

A ideia, de DeMillo, Lipton e Sayward (1978): **injete defeitos artificiais no código** e
veja se a suíte os pega.

- mutante **morto** = algum teste ficou vermelho. ✅
- mutante **sobrevivente** = nenhum teste percebeu. ❌ Há uma lacuna.
- **escore de mutação** = mortos / total.

O escore de mutação é uma medida da **qualidade da suíte**; a cobertura é uma medida do
**alcance** dela.

### 4.1 Experimento real no projeto-modelo

Sete mutações aplicadas à mão em [`07-projeto-modelo/python/`](07-projeto-modelo/README.md),
com a suíte de 190 testes (cobertura 98,7 %). Executado em 13/08/2026:

| # | Mutação | Resultado | Testes vermelhos |
|---|---|---|---|
| M1 | `hoje >= self.proxima_cobranca` → `>` | **morto** ✅ | **18** |
| M2 | `MAX_TENTATIVAS = 3` → `4` | **morto** ✅ | 1 |
| M3 | `ROUND_HALF_UP` → `ROUND_DOWN` no desconto | **morto** ✅ | 4 |
| M4 | remover `historico.append("pausada")` | **SOBREVIVEU** ❌ | 0 |
| M5 | `timeout: float = 5.0` → `500.0` | **SOBREVIVEU** ❌ | 0 |
| M6 | ordenar `listar_vencidas` por cliente em vez de por id | **SOBREVIVEU** ❌ | 0 |
| M7 | `"Pagamento confirmado"` → `"Pagamento OK"` | **morto** ✅ | 1 |

Escore: **4/7 ≈ 57 %** nesta amostra pequena e enviesada (escolhi mutações interessantes, não
aleatórias). O que ela revela é mais útil que o número:

**M1 matou 18 testes.** A fronteira do vencimento é o coração do sistema, e a suíte está
densa ali. Bom sinal.

**M3 matou 4, e três deles são os casos de fronteira** (`1999`, `1`, `3` centavos). Sem os
casos de meio-centavo, a mutação teria sobrevivido — os testes de valores redondos
(`1000, 10 → 900`) não distinguem `ROUND_HALF_UP` de `ROUND_DOWN`.

**M4 sobreviveu**, e está **certo assim.** O histórico é diagnóstico, não comportamento
observável. Escrever teste para ele acoplaria a suíte a um detalhe. Decisão consciente.

**M5 sobreviveu**, e é uma **lacuna real** — do lado Python. O timeout do gateway não é
verificado por nenhum teste, então um erro de digitação (`500.0`) passaria. O lado
JavaScript **mata** este mutante, com o teste `respeita o timeout e aborta` do
`gateway.integracao.test.js`. É a diferença entre esqueleto de I/O não testado e I/O testado
contra servidor real.

**M6 sobreviveu**, e é a lacuna mais interessante das três: o teste
`test_ordena_por_id_para_ser_deterministico` existe, mas usa ids `a`, `b`, `c` com clientes
`a@ex.br`, `b@ex.br`, `c@ex.br` — que ordenam **igual**. O teste está lá, parece cobrir, e
não distingue as duas implementações. **Este é o tipo de defeito de teste que só a análise de
mutação encontra**, e nenhuma métrica de cobertura acusaria.

> **Correção derivada do experimento:** usar dados que quebrem a coincidência —
> id `a1` com cliente `zeca@ex.br`, id `a2` com cliente `ana@ex.br`. Se você estiver
> estudando com este material, é um bom exercício aplicar essa correção e reexecutar M6.

### 4.2 Ferramentas

| Linguagem | Ferramenta | Situação em 2026 |
|---|---|---|
| Python | **`mutmut`** | mantido, o mais usado |
| Python | **`cosmic-ray`** | mantido; tem sessões, execução distribuída, retomada |
| JavaScript/TS | **Stryker** | maduro, com relatório HTML |
| Java | PIT | o mais maduro do campo |

```bash
pip install mutmut && mutmut run && mutmut results
npx stryker run
```

### 4.3 O custo, e como conviver com ele

Mutação é **cara**: a suíte roda uma vez por mutante. Uma suíte de 2 s com 400 mutantes leva
mais de 13 minutos. Estratégias:

1. **rode só no núcleo crítico** (o módulo de dinheiro, não o de log);
2. **rode só sobre o diff** (`mutmut run --paths-to-mutate` no que mudou);
3. **rode semanalmente**, não a cada commit;
4. **use como diagnóstico, não como portão** — um limite de escore de mutação no CI produz
   testes escritos para matar mutante, que é uma forma nova de métrica capturada.

---

## 5. Que número de cobertura perseguir?

Recomendação honesta, por tipo de código:

| Código | Alvo | Por quê |
|---|---|---|
| domínio, regras de negócio, cálculo | **90–100 %** com ramo | é onde os bugs custam |
| casos de uso / serviços | 80–90 % | orquestração; teste os caminhos |
| adaptadores (HTTP, banco, fila) | 50–70 % | I/O; um teste de integração cobre muito |
| borda (CLI, `main`, montagem) | 0–30 % | forçar cobertura aqui produz teste de mentira |
| código gerado, migrações | 0 % | exclua da medição |

**Um número global de 100 % é um erro de gestão**, não um objetivo. Ele empurra o time a
escrever testes triviais para as partes fáceis, enquanto a parte difícil continua sem
verificação de qualidade.

O projeto-modelo tem `fail_under = 90` e cobertura real de 98,7 %, com **quatro linhas
deliberadamente não cobertas** e marcadas com `# pragma: no cover` — o corpo HTTP do gateway
e o `if __name__ == "__main__"`. Cobri-las exigiria um teste que não verificaria nada.

---

## 6. A lei de Goodhart aplicada a testes

> **"Quando uma medida se torna uma meta, ela deixa de ser uma boa medida."**
> — Charles Goodhart (formulação de Marilyn Strathern, 1997)

O que acontece quando a cobertura vira meta de time, na ordem observada na prática:

1. testam-se getters, `__repr__`, constantes;
2. escrevem-se testes sem asserção, só para executar linhas;
3. exclui-se do relatório o código difícil ("é só configuração");
4. o número sobe, a qualidade cai, e ninguém pode dizer isso em voz alta;
5. quando um bug escapa, a resposta é aumentar a meta.

**A saída:** use cobertura como **detector de lacunas**, olhando o relatório
`term-missing` — "estas 12 linhas nunca rodaram, isso é intencional?" —, não como número no
painel. E, se precisar de um portão no CI, ponha o limite **baixo** (60–70 %) e trate-o como
alarme de incêndio, não como meta.

---

## 7. Métricas que valem mais que cobertura

Em ordem de utilidade prática:

| Métrica | O que revela | Como medir |
|---|---|---|
| **tempo da suíte rápida** | se as pessoas rodam ou não | `pytest --durations=10` |
| **taxa de instabilidade** (*flaky rate*) | se o vermelho significa algo | reexecuções por semana no CI |
| **bugs que escaparam para produção** | eficácia real da suíte | *post-mortem*: "que teste teria pego?" |
| **tempo até o vermelho** | qualidade do laço de feedback | do commit ao alerta |
| **escore de mutação no núcleo** | qualidade das asserções | mutmut/Stryker, mensal |
| **cobertura de ramo do diff** | se o código **novo** está testado | `diff-cover`, relatórios de PR |

A última é a mais subestimada: **cobertura do diff** em vez de cobertura global. Ela pergunta
*"o que você escreveu hoje está testado?"* — que é acionável — em vez de *"quanto do sistema
inteiro está coberto?"* — que ninguém consegue mudar num PR.

```bash
pip install diff-cover
pytest --cov --cov-report=xml
diff-cover coverage.xml --compare-branch=main --fail-under=80
```

---

## 8. Interpretando o relatório

```
Name                         Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------
assinaturas/assinatura.py       61      0     12      0   100%
assinaturas/cli.py              47      1      8      1    96%   81
assinaturas/gateway.py          32      3      2      0    91%   36-38
assinaturas/servico.py          66      0     10      0   100%
------------------------------------------------------------------------
TOTAL                          341      4     54      1    99%
```

| Coluna | Significa |
|---|---|
| `Stmts` | comandos executáveis |
| `Miss` | comandos nunca executados |
| `Branch` | ramos possíveis |
| `BrPart` | ramos tomados **só num sentido** ← olhe esta coluna |
| `Missing` | os números de linha, para você ir ver |

**`BrPart` é a coluna que ninguém olha e a que mais informa.** Um `if` que só foi testado no
caminho verdadeiro aparece aqui, mesmo com 100 % de linha.

**Como usar de verdade:** gere o relatório HTML e **leia o código vermelho**.

```bash
pytest --cov --cov-report=html && xdg-open htmlcov/index.html
```

Para cada trecho não coberto, uma de três respostas:
1. "falta teste" → escreva;
2. "é impossível de acontecer" → então **apague o código**;
3. "é I/O sem lógica" → marque `# pragma: no cover` com o motivo escrito.

A resposta nº 2 é a mais valiosa e a menos usada: cobertura é uma excelente ferramenta de
**detecção de código morto**.

---

## 9. Os cinco porquês: por que 100 % de cobertura não garante qualidade?

**1. Por quê?** Porque cobertura mede execução, não verificação.

**2. Por que a execução não basta?** Porque um teste sem asserção — ou com asserção fraca —
executa tudo e não julga nada. O modelo RIP explica: cobertura compra a *Reachability* e
ignora *Infection* e *Propagation*.

**3. Por que não medir a verificação diretamente?** Porque "esta asserção é forte o
suficiente?" exige saber qual é a resposta certa para toda entrada — que é o **problema do
oráculo** ([10-fundamentos.md](10-fundamentos.md) §8). Não há como computar isso em geral.

**4. Então por que a análise de mutação funciona?** Porque ela troca a pergunta impossível
por uma pergunta operacional: *"se eu estragar o código de um jeito plausível, a suíte
percebe?"* Ela mede a **sensibilidade** da suíte a defeitos, que é uma aproximação
verificável da força das asserções.

**5. Por que então a mutação também não é a métrica definitiva?** Porque ela depende dos
**operadores de mutação** disponíveis, que são defeitos sintáticos simples. Ela se apoia em
duas hipóteses: a do **programador competente** (os defeitos reais são pequenos desvios de um
programa quase certo) e o **efeito de acoplamento** (uma suíte que pega defeitos simples pega
também os complexos). Ambas têm apoio empírico e **nenhuma é um teorema**.

**Parada legítima: é o problema do oráculo, que é indecidível em geral.** Não existe, nem
pode existir, uma métrica computável que decida se uma suíte é "boa". Todas as métricas são
aproximações com vieses conhecidos — e é por isso que usá-las como meta produz exatamente o
comportamento que a lei de Goodhart prevê.

---

## Autoteste

1. Escreva um teste com 100 % de cobertura que não verifica nada.
2. Diferencie cobertura de linha, de ramo e de condição no exemplo `idade >= 60 and tem_convenio`.
3. O que é MC-DC e onde ele é exigido por norma?
4. Por que a cobertura não pode acusar "código ausente"? Dê um exemplo.
5. Explique o modelo RIP e qual das três condições a cobertura compra.
6. No experimento, por que M6 sobreviveu apesar de existir um teste de ordenação?
7. Por que M4 sobreviveu e isso está certo?
8. Cite três estratégias para conviver com o custo da análise de mutação.
9. Por que um alvo global de 100 % é um erro de gestão?
10. Descreva a sequência de degradação prevista pela lei de Goodhart aplicada a cobertura.
11. Por que cobertura do **diff** é mais acionável que cobertura global?
12. O que a coluna `BrPart` mostra e por que ela é a mais informativa?
13. Percorra os cinco porquês até a parada legítima e explique por que nenhuma métrica pode ser definitiva.
