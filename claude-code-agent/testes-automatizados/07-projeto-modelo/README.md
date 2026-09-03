# Projeto-modelo — cobrança recorrente de assinaturas

`Nível: iniciante → intermediário` · `Escrito e executado em 12/08/2026`

Uma aplicação pequena, **inteira e executável**, implementada **duas vezes**: em Python e
em JavaScript. Mesmo domínio, mesmas regras, mesmos nomes de teste. Ler os dois lado a lado
é o exercício central deste assunto: você vê que **o raciocínio de teste é o mesmo** e que
só muda a sintaxe.

| | Python | JavaScript |
|---|---|---|
| Corredor de testes | pytest 9.1.1 | `node:test` (embutido) + Vitest 4.1.10 |
| Linguagem | Python 3.10.12 | Node.js 24.18.0 (ESM) |
| Dependências de produção | **nenhuma** | **nenhuma** |
| Dependências de teste | pytest, pytest-cov, hypothesis | nenhuma (Vitest é opcional) |
| Testes | **190 passando** | **245 passando** |
| Cobertura (linha + ramo) | 98,7 % | 100 % linha / 98,4 % ramo |
| Suíte rápida | 1,98 s | 0,29 s |

> Todos os números acima foram medidos nesta máquina, em 12/08/2026, e estão reproduzidos
> ao final deste arquivo com a saída literal dos comandos.

---

## 1. O que o programa faz

Uma empresa vende assinaturas mensais e anuais. Todo dia, uma rotina precisa:

1. achar as assinaturas cujo vencimento chegou;
2. cobrar cada uma no gateway de pagamento;
3. se aprovar → empurrar o vencimento um ciclo, contar o ciclo, avisar o cliente;
4. se recusar → contar a tentativa; **na terceira**, cancelar a assinatura;
5. se o **gateway cair** → não punir ninguém, avisar e tentar amanhã.

O passo 5 é o coração didático do projeto. Ele separa duas coisas que parecem iguais e não
são: *"o cartão do cliente foi recusado"* (culpa do cliente, conta tentativa) e *"o provedor
está fora do ar"* (culpa nossa, **não** conta). Confundir os dois já cancelou assinatura de
gente pagante em empresa de verdade, durante um incidente de 20 minutos.

## 2. Por que este domínio, e não uma calculadora

Um tutorial de teste com `soma(2, 2) == 4` ensina a sintaxe e esconde o problema real. Este
domínio foi escolhido porque força você a lidar com as **quatro coisas difíceis de testar**:

| Coisa difícil | Onde aparece | Como o projeto resolve |
|---|---|---|
| **Dinheiro** | `dinheiro.py` / `dinheiro.js` | centavos inteiros, arredondamento explícito e testado |
| **Tempo** | `relogio.py` / `relogio.js` | relógio injetado; nada chama `date.today()` no meio da regra |
| **Rede** | `gateway.py` / `gateway.js` | contrato + fake + dublê que explode; um teste de integração com servidor HTTP real |
| **Banco** | `repositorio.py` / `repositorio.js` | fake em memória + SQLite real, **os dois** validados pela mesma bateria de contrato |

Se você souber testar essas quatro, o resto é detalhe.

## 3. Estrutura

```
07-projeto-modelo/
├── README.md                        ← você está aqui
│
├── python/
│   ├── pyproject.toml               configuração do pytest e do coverage, comentada linha a linha
│   ├── assinaturas/
│   │   ├── dinheiro.py              domínio puro: valor em centavos, desconto, formatação
│   │   ├── plano.py                 catálogo, cupons, aritmética de calendário
│   │   ├── assinatura.py            máquina de estados (ativa/pausada/inadimplente/cancelada)
│   │   ├── relogio.py               Protocol + RelogioDoSistema + RelogioFixo (stub)
│   │   ├── gateway.py               Protocol + GatewayHttp + GatewayFalso (fake) + GatewayQueExplode
│   │   ├── repositorio.py           Protocol + RepositorioMemoria (fake) + RepositorioSQLite (real)
│   │   ├── servico.py               caso de uso: recebe as 4 dependências por injeção
│   │   └── cli.py                   borda: só monta objetos e imprime (zero regra)
│   └── tests/
│       ├── conftest.py              fixtures compartilhadas
│       ├── test_dinheiro.py         unitário puro, parametrize, fronteiras de arredondamento
│       ├── test_plano.py            catálogo, calendário, ano bissexto
│       ├── test_cupom.py            teste de fronteira (o "vale até dia 31" resolvido)
│       ├── test_assinatura.py       tabela de transições + meta-teste de completude
│       ├── test_relogio.py          como (não) testar o relógio do sistema
│       ├── test_servico.py          dublês: stub, fake, spy, mock, autospec
│       ├── test_contrato_repositorio.py   a MESMA bateria no fake e no SQLite
│       ├── test_repositorio_sqlite.py     integração, marcada com @pytest.mark.integracao
│       ├── test_propriedades.py     property-based com Hypothesis
│       └── test_cli.py              smoke test da borda com capsys
│
└── javascript/
    ├── package.json                 scripts: test, test:unit, test:integracao, test:cov, test:vitest
    ├── vitest.config.js             configuração comentada do Vitest 4
    ├── src/
    │   ├── dinheiro.js              + o problema extra do JS: não existe tipo inteiro
    │   ├── data.js                  datas ISO como texto — e os cinco porquês de não usar Date
    │   ├── plano.js · assinatura.js · relogio.js · gateway.js · repositorio.js · servico.js
    │   └── cli.js                   usa `parseArgs` e `import.meta.main` (Node 24)
    ├── test/                        node:test — zero dependência
    │   ├── dinheiro.test.js         + tabela de tradução pytest → node:test
    │   ├── data.test.js             a armadilha de fuso horário, com teste
    │   ├── plano.test.js · assinatura.test.js · relogio.test.js · servico.test.js
    │   ├── contratoRepositorio.test.js
    │   ├── cli.test.js
    │   ├── gateway.integracao.test.js      HTTP contra servidor REAL em localhost
    │   ├── repositorio.integracao.test.js  SQLite via node:sqlite
    │   └── cli.integracao.test.js          executa o binário num processo separado
    └── vitest/                      os mesmos testes traduzidos para Vitest
        ├── dinheiro.vitest.js       + tabela de tradução node:test → Vitest/Jest
        └── servico.vitest.js        vi.fn, vi.spyOn, vi.useFakeTimers
```

---

## 4. Como rodar — Python

Pré-requisito: Python 3.10 ou superior (`python3 --version`).

```bash
cd testes-automatizados/07-projeto-modelo/python

# 1. Ambiente isolado. Nunca instale pacote de projeto no Python do sistema.
python3 -m venv .venv

# 2. Ativar. No Windows (PowerShell): .venv\Scripts\Activate.ps1
source .venv/bin/activate

# 3. Instalar o projeto em modo editável + as ferramentas de teste
pip install -e '.[dev]'

# 4. Rodar tudo
pytest
```

Saída esperada (a real desta máquina, em 12/08/2026):

```
190 passed in 3.77s
```

Comandos do dia a dia:

```bash
pytest                          # tudo
pytest -m "not integracao"      # só o rápido: 175 testes em ~2 s
pytest -x                       # para no primeiro erro
pytest -k "cupom"               # só o que casa com "cupom" no nome
pytest tests/test_dinheiro.py::TestDesconto   # uma classe
pytest -q --cov                 # com relatório de cobertura
pytest --lf                     # só os que falharam da última vez
pytest -vv                      # nome de cada teste, um por linha

python -m assinaturas.cli demo  # ver o programa rodando
```

## 5. Como rodar — JavaScript

Pré-requisito: Node.js 24 ou superior (`node --version`). **Nada para instalar.**

```bash
cd testes-automatizados/07-projeto-modelo/javascript

node --test                     # 245 testes, zero dependência
```

Saída esperada (real, 12/08/2026):

```
ℹ tests 245
ℹ pass 245
ℹ fail 0
```

Comandos do dia a dia:

```bash
npm test                        # = node --test
npm run test:unit               # 220 testes em ~290 ms
npm run test:integracao         # 25 testes que tocam disco/rede local
npm run test:watch              # re-roda ao salvar
npm run test:cov                # cobertura via V8, sem instrumentação

npm run demo                    # ver o programa rodando
```

A variante em Vitest é **opcional** e a única coisa neste projeto que exige `npm install`:

```bash
npm install                     # baixa o Vitest 4 (44 pacotes)
npm run test:vitest             # 52 testes
```

---

## 6. O que cada decisão de projeto ensina

### 6.1 Dinheiro em centavos inteiros

`0.1 + 0.2 !== 0.3` nas duas linguagens. Em JavaScript é pior: `19.99 * 100` dá
`1998.9999999999998`, e não existe tipo inteiro para se refugiar. A solução — inteiros de
centavos, conversão feita **em texto** e não com `parseFloat`, arredondamento
meio-para-cima explícito — está travada por teste, incluindo o caso `R$ 19,99 com 10%`,
onde o desconto exato é 199,9 centavos e alguém tem de perder um centavo.

**Ensina:** o teste é onde uma decisão de negócio (quem fica com o centavo) vira executável.

### 6.2 O relógio entra pelo construtor

Nenhuma regra chama `date.today()` / `new Date()`. Quem precisa da data recebe um objeto
`Relogio`. Testar vira trivial: passe `RelogioFixo("2026-08-12")`.

A alternativa — congelar o tempo global (`freezegun`, `vi.useFakeTimers`, `t.mock.timers`) —
está demonstrada em `test/relogio.test.js`, porque às vezes é a única saída em código
legado. Mas o projeto **prefere a injeção**, e diz por quê: tempo falso global vaza entre
testes e produz falha por ordem de execução, o pior tipo de defeito de suíte.

**Ensina:** testabilidade é consequência de design, não de ferramenta.

### 6.3 Contratos com quatro tipos de dublê

| Dublê | Classe | O que faz | Como o teste verifica |
|---|---|---|---|
| **stub** | `RelogioFixo` | responde valor fixo | não verifica nada nele |
| **fake** | `GatewayFalso`, `RepositorioMemoria` | implementação funcional simplificada | verifica **estado** depois |
| **spy** | `NotificadorEspiao` | registra as chamadas | verifica a lista de mensagens |
| **mock** | `Mock()` / `vi.fn()` | verifica interação exata | `assert_called_once_with` |
| **sabotador** | `GatewayQueExplode` | falha de propósito | verifica o caminho triste |

Regra adotada e escrita no código: **verificar estado sempre que possível, interação só
quando o efeito colateral é o comportamento** (cobrar, enviar e-mail). Mock demais amarra o
teste à implementação e faz refatoração quebrar teste verde.

### 6.4 Teste de contrato: o antídoto para o fake mentiroso

`test_contrato_repositorio.py` e `contratoRepositorio.test.js` rodam **a mesma bateria** no
fake em memória e no SQLite real. É o que impede o cenário clássico: os unitários passam
com o fake, a produção quebra porque o SQL estava errado.

E o teste `divergência conhecida entre as implementações` documenta, com código, a única
diferença que sobrou (o fake guarda referências, o SQLite guarda cópias) em vez de escondê-la
num comentário.

**Ensina:** todo dublê é uma hipótese sobre o mundo real. Contrato é como se verifica a hipótese.

### 6.5 A pirâmide, na prática

| Camada | Quantos | Tempo | O que cobre |
|---|---|---|---|
| Unitário puro | ~190 (Py) / ~220 (JS) | < 300 ms | toda a regra de negócio |
| Integração | 15 (Py) / 25 (JS) | ~1,5 s | SQL, HTTP, arquivo, processo |
| Ponta a ponta | 1 (Py) / 2 (JS) | ~100 ms | o programa executa mesmo |

Repare na proporção e no custo. É a pirâmide de Cohn saindo naturalmente do design, não
imposta por regra.

### 6.6 Coisas que tutorial não põe e projeto real tem

- **tratamento de erro** — o laço de cobrança não aborta no primeiro problema;
- **configuração** — `pyproject.toml` e `package.json` com scripts nomeados e comentados;
- **separação rápido/lento** — marcador `integracao` no pytest, convenção de nome no Node;
- **avisos como erro** — `filterwarnings = ["error"]`, para `DeprecationWarning` virar tarefa;
- **`--strict-markers`** — um typo em `@pytest.mark.integraçao` vira **erro**, não um teste
  silenciosamente ignorado;
- **meta-teste** — `test_a_tabela_cobre_todas_as_combinacoes` verifica se o **teste** ficou
  incompleto quando alguém adiciona um estado novo;
- **property-based** — 15 testes de propriedade com Hypothesis; um deles (`ida e volta de
  formatação`) encontrou um bug real de separador de milhar durante a escrita.

---

## 7. Execução verificada, 12/08/2026

Python (`pytest --cov`, com `pytest 9.1.1`, `coverage 7.15.4`, `hypothesis 6.165.3`,
`Python 3.10.12`, Linux):

```
Name                         Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------
assinaturas/__init__.py          9      0      0      0   100%
assinaturas/assinatura.py       61      0     12      0   100%
assinaturas/cli.py              47      1      8      1    96%   81
assinaturas/dinheiro.py         41      0     14      0   100%
assinaturas/gateway.py          32      3      2      0    91%   36-38
assinaturas/plano.py            31      0      8      0   100%
assinaturas/relogio.py          15      0      0      0   100%
assinaturas/repositorio.py      39      0      0      0   100%
assinaturas/servico.py          66      0     10      0   100%
------------------------------------------------------------------------
TOTAL                          341      4     54      1    99%
Required test coverage of 90.0% reached. Total coverage: 98.73%
190 passed in 3.77s
```

As 4 linhas não cobertas são deliberadas e estão marcadas com `# pragma: no cover`: o corpo
de `GatewayHttp.cobrar` (que só faria sentido testar contra um servidor real, como o lado
JavaScript faz) e o `if __name__ == "__main__"` da CLI. **Forçar 100% aqui produziria teste
de mentira** — ver [19-cobertura-e-metricas.md](../19-cobertura-e-metricas.md).

JavaScript (`node --test --experimental-test-coverage`, Node v24.18.0):

```
ℹ tests 245
ℹ pass 245
ℹ fail 0
ℹ ----------------------------------------------------------------
ℹ file            | line % | branch % | funcs % | uncovered lines
ℹ ----------------------------------------------------------------
ℹ  assinatura.js  | 100.00 |   100.00 |  100.00 | 
ℹ  cli.js         |  97.59 |    83.33 |  100.00 | 82-83
ℹ  data.js        | 100.00 |   100.00 |  100.00 | 
ℹ  dinheiro.js    | 100.00 |   100.00 |  100.00 | 
ℹ  gateway.js     | 100.00 |   100.00 |  100.00 | 
ℹ  plano.js       | 100.00 |   100.00 |  100.00 | 
ℹ  relogio.js     | 100.00 |   100.00 |  100.00 | 
ℹ  repositorio.js | 100.00 |    95.83 |  100.00 | 
ℹ  servico.js     | 100.00 |    96.30 |  100.00 | 
ℹ ----------------------------------------------------------------
ℹ all files       | 100.00 |    98.38 |  100.00 | 
ℹ ----------------------------------------------------------------
```

Vitest (`npx vitest run`, Vitest 4.1.10):

```
 Test Files  2 passed (2)
      Tests  52 passed (52)
   Duration  326ms
```

**Não executado neste ambiente:** Windows e macOS (a suíte não tem código dependente de
SO, mas isso não foi verificado); Jest 30 (a tradução Vitest → Jest está documentada em
[17-javascript-vitest-jest.md](../17-javascript-vitest-jest.md), não exercitada aqui).

---

## 8. Exercícios sobre este projeto

Do mais fácil ao mais difícil. Cada um deve começar por um **teste que falha**.

1. Adicione o plano `"trimestral"` (R$ 129,00, 90 dias). Quais testes quebram sozinhos? *(Dica: dois.)*
2. Faça o cupom aceitar percentual com uma casa decimal (12,5 %). Quais decisões de arredondamento o teste força você a tomar?
3. Implemente `Assinatura.reativar()` — só a partir de `CANCELADA`, e só se o cancelamento foi por inadimplência, não por pedido do cliente. Note que isso exige um campo novo. Escreva o teste antes.
4. Faça a cobrança **tentar de novo** uma vez quando o gateway explodir, com espera de 1 segundo. Como você testa a espera sem que a suíte fique 1 s mais lenta?
5. Troque o `RepositorioSQLite` por um `RepositorioPostgres`. Quantos testes você precisa mudar? *(Resposta desejada: nenhum dos unitários; a bateria de contrato ganha uma terceira implementação.)*
6. Rode um mutante: mude `>=` para `>` em `esta_vencida`. Algum teste pega? E se mudar `MAX_TENTATIVAS` de 3 para 4? Isso é *mutation testing* na mão — ver [60-teoria-avancada.md](../60-teoria-avancada.md).

---

## 9. Autoteste

1. Por que o `GatewayQueExplode` existe, se já existe o `GatewayFalso(aprovar=False)`?
2. O que aconteceria se `ServicoRenovacao` chamasse `date.today()` em vez de receber um relógio? Cite duas consequências para os testes.
3. Qual a diferença prática entre `assert.equal` e `assert.deepStrictEqual` para dois `Dinheiro`?
4. Por que a bateria de contrato roda contra o fake **e** contra o SQLite, em vez de só contra o SQLite?
5. O `test_a_tabela_cobre_todas_as_combinacoes` não testa o código de produção. Por que ele vale o esforço?
6. A cobertura Python é 98,73 % e não 100 %. Cite as duas linhas que faltam e explique por que cobri-las seria pior.
7. `npm run test:unit` leva 290 ms e `npm test` leva 550 ms. Que decisão de projeto produz essa diferença, e por que ela importa?
