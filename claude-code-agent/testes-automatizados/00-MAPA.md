# Testes Automatizados — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 13/08/2026`
`Base técnica: pytest 9.1.1 · Python 3.10–3.14 · Node.js 24.18 LTS · Vitest 4.1.10 · Jest 30.4.2`

---

## Suas quatro perguntas, respondidas em 60 segundos

**1. O que são testes automatizados?**

É um **programa que usa o seu programa** e verifica se a resposta é a esperada, sem
intervenção humana, produzindo um veredito binário: verde ou vermelho.

```python
def test_gorjeta_de_dez_por_cento():
    assert calcular_gorjeta(100, 10) == 10
```

Leia em voz alta: *"afirmo que a gorjeta de 10% sobre 100 é 10."* Se for verdade, passa em
silêncio; se for mentira, o programa grita. É isso — todo o resto é profundidade.
*(Detalhe em [01-introducao-leigo.md](01-introducao-leigo.md) e [10-fundamentos.md](10-fundamentos.md).)*

**2. Como fazer, passo a passo?**

```
1. instale o ambiente          → 03-instalacao.md
2. escreva um teste que FALHA  → 04-como-comecar.md
3. faça passar                 → 04-como-comecar.md
4. escolha os casos com método → 10-fundamentos.md §10 (partição e fronteira)
5. isole as dependências       → 14-dubles-de-teste.md
6. rode a cada salvamento      → 05-manual-de-uso.md
7. rode no CI a cada envio     → 21-ci-e-automacao.md
```

Do zero à primeira luz verde: **40 minutos**, incluindo instalação.

**3. O que são testes unitários?**

São **uma espécie** dentro do gênero "testes automatizados": o teste de um pedaço isolado do
programa. A definição operacional deste curso, que evita a briga de 26 anos sobre o que é uma
"unidade":

> Um teste é **unitário** se: **(a)** verifica um comportamento, **(b)** roda em
> milissegundos, **(c)** não toca banco, rede, disco nem relógio, e **(d)** roda em qualquer
> ordem junto com os outros.

As outras espécies são **integração** (duas peças conversando, ou uma dependência real) e
**ponta a ponta** (o sistema inteiro, como o usuário usa).
*(Detalhe em [12-tipos-e-piramide.md](12-tipos-e-piramide.md) e [13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md).)*

**4. Como fazer em Python? E em JavaScript?**

| | Python | JavaScript |
|---|---|---|
| ferramenta | **pytest** (instalar) | **`node:test`** (já vem no Node) |
| um teste | `def test_x():` | `test('x', () => {})` |
| asserção | `assert a == b` | `assert.equal(a, b)` |
| explode | `with pytest.raises(E):` | `assert.throws(fn, E)` |
| rodar | `pytest` | `node --test` |

```python
# Python
def test_soma():
    assert somar(2, 2) == 4
```

```javascript
// JavaScript
import assert from 'node:assert/strict';
import { test } from 'node:test';

test('soma', () => {
  assert.equal(somar(2, 2), 4);
});
```

**O raciocínio é idêntico; só muda a sintaxe.** É por isso que este curso implementa o mesmo
projeto nas duas linguagens, lado a lado.
*(Detalhe em [16-python-pytest.md](16-python-pytest.md), [17-javascript-vitest-jest.md](17-javascript-vitest-jest.md), e no [projeto-modelo](07-projeto-modelo/README.md).)*

---

## O que você saberá ao final

- Explicar para alguém de fora o que é um teste automatizado e por que ele existe.
- Instalar o ambiente completo em Linux, macOS ou Windows — ou começar sem instalar nada.
- Escrever testes em Python (pytest) **e** em JavaScript (`node:test`, Vitest, Jest).
- **Escolher os casos com método**: partição de equivalência e valores de fronteira.
- Distinguir e usar corretamente os cinco dublês: dummy, stub, spy, mock e fake.
- Saber **quando não usar mock** — e por que mock demais destrói a suíte.
- Testar o que é difícil: banco de dados, HTTP, tempo, aleatoriedade, concorrência.
- **Tornar testável um código que não é** — o capítulo que separa quem sabe usar pytest de
  quem sabe testar.
- Ler cobertura sem se enganar, e medir a força da suíte com análise de mutação.
- Escrever testes de propriedade que encontram bugs que você não imaginou.
- Montar CI, domar testes instáveis e manter a suíte rápida ao longo dos anos.
- Discutir com fundamento: pirâmide × troféu, clássica × mockista, TDD sim ou não.
- Entender os limites teóricos: problema do oráculo, indecidibilidade, o que testes **não**
  podem provar.

---

## Roteiro de leitura

### Rota rápida — "quero escrever meu primeiro teste hoje" (2 h)

```
01 → 03 → 04 → 06
```

### Rota completa — do zero ao autônomo (~65 h com prática)

```
Bloco A   01 → 02 → 03 → 04 → 05 → 06 → 07-projeto-modelo
Bloco B   10 → 11 → 12 → 13 → 14 → 15 → 16/17 → 18 → 19 → 20 → 21
Bloco C   70 (12 laboratórios) → 75
Bloco D   80 → 85
Bloco E   90 → 95
```

### Rota para quem já testa há anos

```
13 (clássica × mockista) → 14 (dublês) → 19 (mutação) → 20 (testabilidade)
→ 60 (teoria) → 65 (estado da arte)
```

### Se você só puder ler três arquivos

1. **[20-testabilidade-e-design.md](20-testabilidade-e-design.md)** — onde quase todo mundo trava.
2. **[13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md)** — o que é "unidade", de verdade.
3. **[19-cobertura-e-metricas.md](19-cobertura-e-metricas.md)** — por que os números enganam.

---

## Os arquivos

### Bloco A · Porta de entrada

| Arquivo | O que tem |
|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | a analogia da fábrica de torneiras; zero jargão; o caso do centavo |
| [02-pre-requisitos.md](02-pre-requisitos.md) | o que saber antes, tempo realista por nível, rota de resgate |
| [03-instalacao.md](03-instalacao.md) | manual de campo: Linux, macOS, Windows nativo **e** WSL2; `uv`, `nvm`, PATH, permissões, proxy, desinstalação, tabela de erros literais, **alternativa sem instalar nada** |
| [04-como-comecar.md](04-como-comecar.md) | do ambiente pronto à primeira luz verde, nas duas linguagens, com as saídas reais |
| [05-manual-de-uso.md](05-manual-de-uso.md) | referência consultável por tarefa: pytest, `node:test`, Vitest, Jest |
| [06-exemplos.md](06-exemplos.md) | **12 exemplos completos e executados**, do CPF ao teste de API HTTP |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | uma aplicação inteira, **duas vezes**: Python e JavaScript |

### Bloco B · Núcleo

| Arquivo | O que tem |
|---|---|
| [10-fundamentos.md](10-fundamentos.md) | erro × defeito × falha, AAA, modelo RIP, os quatro pilares, partição e fronteira |
| [11-historia.md](11-historia.md) | de Turing (1949) ao pytest 9; por que cada prática existe |
| [12-tipos-e-piramide.md](12-tipos-e-piramide.md) | pirâmide, troféu, losango — e as críticas honestas a cada um |
| [13-teste-unitario-a-fundo.md](13-teste-unitario-a-fundo.md) | o que é "unidade"; clássica × mockista; o que **não** testar |
| [14-dubles-de-teste.md](14-dubles-de-teste.md) | dummy, stub, spy, mock, fake e sabotador; estado × interação |
| [15-tdd.md](15-tdd.md) | o ciclo, um exemplo completo, e onde TDD **não** funciona |
| [16-python-pytest.md](16-python-pytest.md) | pytest por dentro: descoberta, reescrita de asserção, fixtures, mocks |
| [17-javascript-vitest-jest.md](17-javascript-vitest-jest.md) | qual corredor usar; `node:test`, Vitest, Jest; as armadilhas só de JS |
| [18-integracao-e-e2e.md](18-integracao-e-e2e.md) | banco, HTTP, navegador; Testcontainers; as 7 regras de E2E |
| [19-cobertura-e-metricas.md](19-cobertura-e-metricas.md) | os 4 critérios; **experimento de mutação executado**; lei de Goodhart |
| [20-testabilidade-e-design.md](20-testabilidade-e-design.md) | **o arquivo mais importante**: por que o problema é o código, não a ferramenta |
| [21-ci-e-automacao.md](21-ci-e-automacao.md) | pipeline mínimo, GitHub Actions comentado, testes instáveis, portões |
| [60-teoria-avancada.md](60-teoria-avancada.md) | Rice, oráculo, adequação, mutação, propriedades, combinatório, fuzzing, formal |
| [65-estado-da-arte.md](65-estado-da-arte.md) | agosto de 2026: geração por LLM, testar código de IA, instabilidade, o que não mudou |

### Bloco C · Prática e erros

| Arquivo | O que tem |
|---|---|
| [70-pratica.md](70-pratica.md) | **12 laboratórios** progressivos, com critério de pronto e solução |
| [75-armadilhas.md](75-armadilhas.md) | 6 mitos + 16 armadilhas + 4 erros de organização, com "por que persiste" |

### Bloco D · Economia e ecossistema

| Arquivo | O que tem |
|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | licenças, preços de CI e de nuvem de navegadores com **data**, custos ocultos, pilha de custo zero |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | cursos gratuitos **PT / EN / FR** pesquisados; a conversa franca sobre o CTFL |

### Bloco E · Fontes

| Arquivo | O que tem |
|---|---|
| [90-bibliografia.md](90-bibliografia.md) | livros comentados, o que envelheceu, o que é legalmente gratuito, edições em PT |
| [95-referencias.md](95-referencias.md) | papers seminais, docs oficiais, normas, código-fonte, pessoas, **e como este material foi verificado** |
| [GLOSSARIO.md](GLOSSARIO.md) | ~130 termos, com o original em inglês e os falsos amigos |

---

## O projeto-modelo

[`07-projeto-modelo/`](07-projeto-modelo/README.md) — **cobrança recorrente de assinaturas**,
implementada duas vezes, com o mesmo domínio e os mesmos nomes de teste.

| | Python | JavaScript |
|---|---|---|
| corredor | pytest 9.1.1 | `node:test` + Vitest 4.1.10 |
| dependências de produção | **nenhuma** | **nenhuma** |
| testes | **190 passando** | **245** (`node:test`) + **52** (Vitest) |
| cobertura | 98,7 % | 100 % linha / 98,4 % ramo |
| suíte rápida | 1,98 s | 0,29 s |

Ele foi escolhido para forçar as **quatro coisas difíceis de testar**: dinheiro, tempo, rede
e banco. Cobre asserções, parametrização, fixtures, os cinco dublês, teste de contrato,
integração com SQLite, HTTP contra servidor real, propriedades com Hypothesis, e um teste de
fumaça da CLI.

**Tudo foi executado.** Os números acima são reais, medidos em 12–13/08/2026.

---

## As 12 camadas de profundidade

| # | Camada | Onde |
|---|---|---|
| 1 | intuição para leigo | [01](01-introducao-leigo.md) |
| 2 | definição informal | [01](01-introducao-leigo.md) §3 |
| 3 | por que existe | [01](01-introducao-leigo.md) §7 · [11](11-historia.md) |
| 4 | ambiente e primeiro uso | [03](03-instalacao.md) · [04](04-como-comecar.md) |
| 5 | fundamentos formais | [10](10-fundamentos.md) |
| 6 | mecânica interna | [16](16-python-pytest.md) §3 · [17](17-javascript-vitest-jest.md) |
| 7 | implementação prática | [06](06-exemplos.md) · [07](07-projeto-modelo/README.md) |
| 8 | casos de uso reais | [06](06-exemplos.md) ex. 8 e 11 · [18](18-integracao-e-e2e.md) |
| 9 | trade-offs e alternativas | [12](12-tipos-e-piramide.md) · [13](13-teste-unitario-a-fundo.md) · [14](14-dubles-de-teste.md) |
| 10 | economia do assunto | [80](80-custos-e-licencas.md) |
| 11 | profundidade de pesquisa | [60](60-teoria-avancada.md) |
| 12 | estado da arte e fronteira | [65](65-estado-da-arte.md) |

---

## Status

| Bloco | Status | Observação |
|---|---|---|
| **A** · porta de entrada | ✅ | 6 documentos + projeto-modelo executado nas duas linguagens |
| **B** · núcleo | ✅ | 14 documentos, do fundamento à teoria da indecidibilidade |
| **C** · prática e erros | ✅ | 12 laboratórios + 26 armadilhas |
| **D** · economia | ✅ | preços com data; cursos PT/EN/FR pesquisados na web |
| **E** · fontes | ✅ | papers, docs, normas, código, pessoas |
| **Glossário** | ✅ | ~130 termos |

**O que não foi executado, e está declarado:** instalação em Windows e macOS (os comandos
vêm da documentação oficial); Jest 30; Playwright; Testcontainers; os 12 laboratórios de
[70-pratica.md](70-pratica.md).

**A reavaliar:** [65-estado-da-arte.md](65-estado-da-arte.md) e
[80-custos-e-licencas.md](80-custos-e-licencas.md) a cada 6 meses;
[85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) a cada ano (links de vídeo
expiram).

---

## Uma frase para levar

> Testes não provam que o programa está certo. Eles compram **coragem para mudá-lo** — e é
> disso que todo software vivo precisa.
