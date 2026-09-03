# 21 · Integração contínua e automação

`Nível: intermediário` · `Última atualização: 13/08/2026`

Um teste que só roda na sua máquina protege só a sua máquina. CI é o que transforma a suíte
numa garantia de time.

---

## 1. O que CI é, e o que não é

> **Integração contínua** é a prática de integrar o trabalho de todo mundo no tronco
> principal com frequência (idealmente várias vezes ao dia), com verificação automática a
> cada integração.

**Não** é "ter um servidor que roda testes". Isso é uma consequência. A prática é a
frequência de integração; a ferramenta é o que a torna viável.

| Se você... | então você não está fazendo CI |
|---|---|
| mantém um branch por semanas | não |
| ignora o vermelho por dias | não |
| roda os testes só antes da entrega | não |
| tem um "período de estabilização" | não |

---

## 2. O pipeline mínimo que se justifica

```
  push / pull request
        │
        ├──▶ lint + formatação        (segundos)
        ├──▶ verificação de tipos     (segundos)
        ├──▶ testes rápidos           (segundos)   ← falha aqui? pare tudo
        ├──▶ testes de integração     (minutos)
        ├──▶ cobertura do diff        (segundos)
        └──▶ build                    (minutos)
                │
          merge no main
                │
                ├──▶ E2E contra ambiente de teste
                └──▶ deploy
```

**A ordem importa**: coisas rápidas e baratas primeiro. Um erro de formatação não deve
esperar 8 minutos de testes de integração para ser reportado.

---

## 3. GitHub Actions — Python

`.github/workflows/testes.yml`

```yaml
name: testes

on:
  push:
    branches: [main]
  pull_request:

# Cancela execuções antigas do mesmo PR quando um novo push chega.
# Sem isto, três pushes seguidos ocupam três runners fazendo trabalho descartável.
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  rapidos:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false          # não cancele o 3.13 porque o 3.10 falhou
      matrix:
        python: ["3.10", "3.12", "3.14"]
    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
          cache: pip            # reaproveita o download entre execuções

      - run: pip install -e '.[dev]'

      - name: testes rápidos
        run: pytest -m "not integracao" -q --timeout=60

  integracao:
    runs-on: ubuntu-latest
    needs: rapidos              # só roda se os rápidos passarem
    services:
      postgres:
        image: postgres:18-alpine
        env:
          POSTGRES_PASSWORD: teste
        options: >-
          --health-cmd pg_isready
          --health-interval 2s
          --health-retries 30
        ports: ["5432:5432"]
    env:
      DATABASE_URL: postgres://postgres:teste@localhost:5432/postgres
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with: { python-version: "3.14", cache: pip }
      - run: pip install -e '.[dev]'
      - run: pytest -m integracao -q --timeout=300

      - name: cobertura
        run: pytest --cov --cov-report=xml -q
      - uses: codecov/codecov-action@v5
        with:
          files: coverage.xml
```

---

## 4. GitHub Actions — JavaScript

```yaml
name: testes

on: [push, pull_request]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  teste:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node: [20, 22, 24]
    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-node@v5
        with:
          node-version: ${{ matrix.node }}
          cache: npm

      # `npm ci` (e NÃO `npm install`): instala exatamente o lockfile e FALHA
      # se ele divergir do package.json. É o que impede o CI de testar um
      # conjunto de versões diferente do que você testou localmente.
      - run: npm ci

      - run: npm run test:unit

      - run: npm run test:integracao

      - name: cobertura
        if: matrix.node == 24
        run: npm run test:cov
```

---

## 5. As sete decisões que fazem o CI valer a pena

### 5.1 Separe rápido de lento em jobs diferentes

Um `job` de 30 segundos que falha cedo dá retorno em 30 segundos. Se tudo estiver num job só,
você espera 8 minutos para descobrir um erro de digitação.

### 5.2 Ponha timeout em tudo

```yaml
jobs:
  teste:
    timeout-minutes: 15
```

```bash
pytest --timeout=60          # pytest-timeout
node --test --test-timeout=60000
```

Sem timeout, um teste travado consome o runner até o limite da plataforma (6 h no GitHub
Actions) e queima a cota do mês.

### 5.3 Cache com chave correta

```yaml
- uses: actions/setup-python@v6
  with: { cache: pip }          # a ação já cuida da chave
```

Cache mal configurado é pior que nenhum: uma chave que não muda quando as dependências mudam
faz o CI testar versões antigas em silêncio.

### 5.4 Matriz de versões — mas só onde faz sentido

| Situação | Matriz |
|---|---|
| biblioteca publicada | **sim** — versões mínima, corrente e a próxima |
| aplicação com deploy controlado | **não** — teste na versão que você entrega |
| suporte a vários SOs | sim, se você realmente suporta |

Matriz custa tempo de runner. Uma aplicação que roda em Node 24 em produção não ganha nada
sendo testada em 3 versões.

### 5.5 Cobertura do diff, não global

```bash
pytest --cov --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
```

Pergunta acionável ("o que você escreveu está testado?") em vez de inacionável ("quanto do
sistema está coberto?").

### 5.6 Artefatos das falhas

```yaml
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: rastro-playwright
    path: |
      playwright-report/
      test-results/
```

Uma falha só no CI, sem rastro, é indepurável. Isso vale para relatório do Playwright,
captura de tela, log do banco e o XML do JUnit.

### 5.7 Falhe também nos avisos

```toml
filterwarnings = ["error"]
```

```yaml
- run: npm run lint -- --max-warnings=0
```

Aviso que ninguém lê acumula até virar 400 linhas de ruído. Trate cada um na hora ou
silencie explicitamente, com motivo e prazo.

---

## 6. Testes instáveis (*flaky*) em CI

### 6.1 Por que aparecem justamente no CI

| Causa | Por que só lá |
|---|---|
| paralelismo | sua máquina roda 1 job; o CI roda 8 |
| máquina mais lenta | timeouts que passavam localmente estouram |
| ordem diferente | a ordem de coleta pode variar |
| fuso e locale | o runner é UTC, `C.UTF-8` |
| rede | latência e DNS diferentes |
| estado limpo | o CI não tem o cache/banco que você tem local |

### 6.2 Como tratar

1. **Meça.** Guarde os resultados por teste; um teste que falhou 3 vezes no mês é *flaky*,
   não azar.
2. **Quarentena, com prazo.** Marque, tire do portão, e crie a tarefa com data. Quarentena
   sem prazo é cemitério.
3. **`retries` só como analgésico.** No Playwright, `retries: 2` em CI e `0` local. Junto com
   um painel do que precisou repetir.
4. **Conserte a causa.** Quase sempre é uma das cinco fontes de indeterminismo
   ([10-fundamentos.md](10-fundamentos.md) §6.3).

**Regra de ouro:** um teste instável não pode continuar bloqueando o merge. Ou você conserta,
ou tira do portão — nunca "reroda até passar", que é como o time aprende a ignorar o
vermelho.

---

## 7. Ganchos locais (pre-commit)

O CI é a rede final; o gancho local é o que evita a ida e volta.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: local
    hooks:
      - id: testes-rapidos
        name: testes rápidos
        entry: pytest -m "not integracao" -q -x
        language: system
        pass_filenames: false
```

```bash
pip install pre-commit && pre-commit install
```

**Regra:** no gancho de commit, **só** o que roda em poucos segundos. Um gancho lento é
desinstalado pelo time em uma semana — e aí você não tem nem gancho nem disciplina.

---

## 8. Portões de merge

Configuração recomendada no GitHub (Settings → Branches → Branch protection):

- [x] exigir que os checks passem antes do merge;
- [x] exigir que o branch esteja atualizado com o `main`;
- [x] exigir revisão de pelo menos uma pessoa;
- [ ] **não** exija cobertura global mínima (ver [19](19-cobertura-e-metricas.md) §6);
- [x] exija cobertura **do diff**, se quiser um número.

**Sobre "exigir branch atualizado":** ele evita o *semantic merge conflict* — dois PRs que
passam isoladamente e quebram juntos, porque um renomeou o que o outro passou a usar. O custo
é ter de reexecutar o CI a cada merge no `main`. Em repositório movimentado, use a **fila de
merge** (*merge queue*), que faz isso automaticamente.

---

## 9. Quanto custa

Preços consultados em **13/08/2026** — confira antes de decidir, mudam com frequência.

| Plataforma | Camada gratuita | Depois |
|---|---|---|
| **GitHub Actions** | ilimitado em repositório **público**; 2.000 min/mês em privado (Free) | por minuto, com multiplicador por SO |
| **GitLab CI** | minutos de *compute* mensais no plano Free | por pacote de minutos |
| **CircleCI** | créditos mensais no plano Free | por crédito |

**Multiplicadores de minuto no GitHub Actions** (a armadilha que pega todo mundo): Linux
conta 1×, **Windows 2×**, **macOS 10×**. Uma matriz com macOS consome a cota dez vezes mais
rápido. Se você não precisa testar em macOS, não teste.

**As três formas de reduzir custo, em ordem de eficácia:**

1. `concurrency` com `cancel-in-progress` — corta o desperdício de pushes seguidos;
2. matriz enxuta — só as versões que você realmente suporta;
3. cache de dependências.

Detalhes e alternativas em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 10. Os cinco porquês: por que a suíte precisa rodar no CI, e não só na máquina?

**1. Por quê?** Porque "na minha máquina funciona" é verdade e irrelevante.

**2. Por que é irrelevante?** Porque a sua máquina tem estado que a de produção não tem:
variáveis de ambiente antigas, um banco com dados de ontem, uma versão de biblioteca que
você instalou em março e esqueceu.

**3. Por que esse estado escondido existe?** Porque o ambiente de desenvolvimento é
**incremental por natureza** — você instala coisas ao longo de meses e nunca recomeça do
zero. O CI, ao contrário, começa de uma imagem limpa toda vez.

**4. Por que ninguém simplesmente recria o ambiente local de vez em quando?** Porque custa
horas e não dá benefício imediato visível. É a mesma economia comportamental do TDD: o custo
é agora, o benefício é depois, e o depois é de outra pessoa.

**5. Então CI é fundamentalmente o quê?** É a **reprodutibilidade terceirizada para uma
máquina que não tem memória**. Ele não é sobre automação — é sobre garantir que a verificação
aconteça num ambiente cujo estado é conhecido e recriável.

**Parada legítima: é uma consequência da irreversibilidade da instalação de software.**
Ambientes acumulam entropia; a única defesa conhecida é recriá-los do zero, e a única forma
sustentável de recriá-los do zero é automatizando. É a mesma razão de existirem containers,
lockfiles e infraestrutura como código.

---

## 11. Além do CI: outras automações que valem

| Automação | Ferramenta | Ganho |
|---|---|---|
| atualização de dependências | Dependabot, Renovate | PR automático com a suíte rodando |
| verificação de vulnerabilidades | `pip-audit`, `npm audit`, CodeQL | dívida de segurança visível |
| análise estática | Ruff, mypy, ESLint, TypeScript | erros pegos sem escrever teste |
| formatação | Ruff format, Prettier | acaba o debate de estilo no PR |
| mutação, semanal | mutmut, Stryker | qualidade da suíte ao longo do tempo |
| detecção de teste lento | `--durations` num relatório | evita a erosão silenciosa |

O **Dependabot com CI verde** é a combinação de maior retorno desta tabela: a atualização
chega como PR, a suíte roda, e você só olha o que quebrou. Sem suíte, atualizar dependência é
apostar.

---

## Autoteste

1. Qual é a definição de CI, e por que "ter um servidor de testes" não é CI?
2. Por que a ordem das etapas do pipeline importa? Dê um exemplo concreto.
3. Para que serve `concurrency: cancel-in-progress` e quanto ele economiza?
4. Por que `npm ci` e não `npm install` no CI?
5. O que acontece sem `timeout-minutes` quando um teste trava?
6. Quando uma matriz de versões se justifica e quando é desperdício?
7. Cite três motivos pelos quais testes instáveis aparecem mais no CI que localmente.
8. Qual é a regra de ouro sobre teste instável bloqueando merge?
9. Por que um gancho de pre-commit lento é pior que nenhum?
10. Quais são os multiplicadores de minuto do GitHub Actions por SO?
11. Percorra os cinco porquês até a parada legítima sobre entropia de ambiente.
12. Por que Dependabot sem suíte de testes tem valor baixo?
