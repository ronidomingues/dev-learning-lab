# 18 · Integração e ponta a ponta

`Nível: intermediário → avançado` · `Última atualização: 13/08/2026`

Onde o teste sai do processo e encosta no mundo: banco, rede, fila, navegador. É a parte
cara da suíte — e a única que prova que o sistema **funciona**.

---

## 1. O que só o teste de integração pega

Testes unitários com dublês não detectam nenhuma destas classes de erro:

| Erro | Exemplo real |
|---|---|
| SQL inválido | `SELECT * FROM assinatura` (tabela é `assinaturas`) |
| serialização | data gravada como `13/08/2026`, comparação `<=` traz lixo |
| tipo do banco | `INTEGER` volta como string; `1 + 1` vira `"11"` |
| transação | dois `UPDATE` sem transação; o segundo falha e o primeiro fica |
| migração | coluna nova sem `DEFAULT`, tabela cheia, `NOT NULL` |
| encoding | `Belém` vira `BelÃ©m` |
| fuso horário | servidor em UTC, banco em `America/Sao_Paulo` |
| contrato HTTP | o parceiro devolve `{"id": 7}`, você espera `{"id": "7"}` |
| autenticação | token expira; ninguém testou o caminho de renovação |
| configuração | variável de ambiente esquecida no ambiente de produção |

Nenhum mock pega isso, **por construção**: um mock devolve o que você mandou, e o que você
mandou é a sua crença sobre o sistema externo — que é justamente o que está errado.

---

## 2. Banco de dados

### 2.1 As quatro estratégias

| Estratégia | Fidelidade | Velocidade | Quando usar |
|---|---|---|---|
| **fake em memória** | baixa | altíssima | testes unitários; exige teste de contrato |
| **SQLite `:memory:`** | média | alta | se o SQL for portável e simples |
| **container descartável** (Testcontainers) | **alta** | média | o padrão em 2026 para banco real |
| **banco compartilhado** | alta | baixa | **evite** — corrida entre testes, estado sujo |

**Recomendação:** container descartável do **mesmo** banco que a produção usa. SQLite no
lugar de Postgres é uma armadilha comum: dialetos divergem em tipos, `UPSERT`, janelas,
JSON, e a mentira só aparece em produção.

### 2.2 Isolamento entre testes: o padrão da transação

O jeito mais rápido de ter isolamento real:

```python
@pytest.fixture(scope="session")
def conexao():
    """Caro: uma conexão para a sessão inteira."""
    return psycopg.connect(URL_DE_TESTE)


@pytest.fixture
def banco(conexao):
    """Barato: cada teste roda dentro de uma transação que é desfeita."""
    conexao.execute("BEGIN")
    yield conexao
    conexao.execute("ROLLBACK")     # desfaz TUDO, inclusive o que deu errado
```

Cada teste vê um banco limpo, e o custo é de microssegundos. As alternativas — `TRUNCATE`
entre testes, ou recriar o esquema — custam de 10 a 1000 vezes mais.

**Limite do padrão:** se o código sob teste gerencia transações por conta própria
(`COMMIT` explícito), o rollback externo não funciona. Aí a saída é `TRUNCATE` das tabelas
tocadas, ou um banco por teste.

### 2.3 Testcontainers

```python
# pip install testcontainers[postgres]
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:18-alpine") as pg:
        yield pg.get_connection_url()
```

```javascript
// npm i -D @testcontainers/postgresql
import { PostgreSqlContainer } from '@testcontainers/postgresql';

let container;
before(async () => {
  container = await new PostgreSqlContainer('postgres:18-alpine').start();
});
after(() => container.stop());
```

**Custo honesto:** exige Docker na máquina e no CI, e o primeiro `start()` leva de 2 a 10
segundos. Por isso: escopo de **sessão**, sempre. Um container por teste é inviável.

### 2.4 Dados de teste

| Abordagem | Prós | Contras |
|---|---|---|
| **fábrica no código** (*object mother*, *builder*) | explícito, tipado, refatorável | escrever |
| **fixture em arquivo** (JSON/YAML/SQL) | fácil de encher | dessincroniza do esquema; ilegível |
| **dump de produção** | realista | **LGPD** — dado pessoal em ambiente de teste é violação |
| **geração aleatória** (Faker) | volume | não determinístico; **fixe a semente** |

**Recomendação:** fábrica no código, com valores padrão sensatos e sobrescrita explícita.

```python
def uma_assinatura(**mudancas) -> Assinatura:
    padrao = dict(id="a1", cliente="ana@ex.br", plano=CATALOGO["pro"], inicio=HOJE)
    return Assinatura(**{**padrao, **mudancas})

# no teste, aparece SÓ o que importa para aquele caso:
a = uma_assinatura(estado=Estado.INADIMPLENTE, tentativas_falhas=2)
```

Isso é o *Object Mother* / *Test Data Builder* de Meszaros. O ganho: o teste mostra o que é
**relevante**, e o resto some.

> **Sobre dump de produção:** além do risco legal (LGPD, art. 7º e 11), é operacionalmente
> ruim — o dump envelhece, é enorme, e ninguém sabe por que aquele registro específico faz
> o teste passar. Se precisar de realismo, use dados **anonimizados e sintetizados** a
> partir da distribuição real, não os dados em si.

---

## 3. HTTP: testar cliente e servidor

### 3.1 Testando o **seu** servidor

Suba o servidor de verdade numa porta efêmera. É barato e fiel — foi o que o
[exemplo 8](06-exemplos.md) fez.

```javascript
await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${servidor.address().port}`;
```

**Nunca fixe a porta.** Dois jobs de CI na mesma máquina brigam por ela, e a falha é
intermitente — o pior tipo.

Em Python, com FastAPI/Flask, use o cliente de teste do próprio framework:

```python
from fastapi.testclient import TestClient

def test_cria_tarefa():
    cliente = TestClient(app)
    resposta = cliente.post("/tarefas", json={"titulo": "café"})
    assert resposta.status_code == 201
    assert resposta.headers["location"].startswith("/tarefas/")
```

> **Atenção:** o `TestClient` **não** sobe um servidor real — ele chama a aplicação ASGI
> diretamente. É rápido e cobre roteamento, validação e serialização, mas **não** cobre a
> camada HTTP de verdade (proxy reverso, cabeçalhos do servidor, HTTP/2). Para isso, um
> teste de fumaça contra o serviço rodando.

### 3.2 Testando o **seu cliente** de uma API alheia

Três níveis, em ordem de fidelidade:

**a) Mock da função de rede** — rápido, frágil, testa a sua crença.

**b) Servidor de mentira local** — o meio-termo recomendado. Você controla as respostas e
exercita a pilha HTTP inteira (foi o que o `gateway.integracao.test.js` do projeto-modelo
fez, com `node:http`).

Em Python, a mesma coisa com `responses`, `respx` (httpx) ou `pytest-httpserver`.

**c) Gravar e reproduzir** (VCR): a primeira execução chama a API de verdade e grava a
resposta em disco; as seguintes reproduzem.

```python
# pip install vcrpy pytest-recording
@pytest.mark.vcr
def test_busca_cep():
    assert buscar_cep("01310-100")["bairro"] == "Bela Vista"
```

| | Vantagem | Risco |
|---|---|---|
| VCR | resposta **real**, sem depender da rede | a gravação envelhece e ninguém percebe |

**Regra de segurança do VCR:** filtre segredos antes de gravar. Um cassete commitado com
`Authorization: Bearer ...` real já vazou credencial em muito repositório público.

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization", "cookie"]}
```

### 3.3 Teste de contrato de consumidor (Pact)

Quando dois times mantêm serviços que conversam, nenhum dos dois consegue testar sozinho.
O padrão **consumer-driven contract**:

1. o **consumidor** escreve o teste declarando o que espera; isso gera um arquivo de contrato;
2. o **produtor** roda esse contrato contra a implementação dele, no CI dele;
3. se o produtor quebrar a expectativa, o CI **dele** fica vermelho — antes do deploy.

É a forma de pegar quebra de contrato entre serviços sem montar um ambiente com todos eles.
Vale a partir de ~3 serviços com times distintos; abaixo disso, o custo de operar o
*broker* de contratos não se paga.

---

## 4. Ponta a ponta com navegador

### 4.1 Ferramentas em 2026

| Ferramenta | Situação |
|---|---|
| **Playwright** 1.62 | **a recomendação** — multi-navegador, auto-espera, rastro, paralelo |
| **Cypress** | ainda popular; roda dentro do navegador, o que limita alguns cenários |
| **Selenium / WebDriver** | padrão W3C; use quando precisar de navegador real remoto ou linguagem sem alternativa |
| **Puppeteer** | só Chrome; hoje é nicho |

### 4.2 Um teste que se sustenta

```javascript
import { expect, test } from '@playwright/test';

test('cliente compra e vê a confirmação', async ({ page }) => {
  await page.goto('/produtos/cafe');

  // Busca por PAPEL e TEXTO VISÍVEL, nunca por classe CSS.
  await page.getByRole('button', { name: 'Adicionar ao carrinho' }).click();
  await page.getByRole('link', { name: 'Finalizar compra' }).click();

  await page.getByLabel('Número do cartão').fill('4111111111111111');
  await page.getByRole('button', { name: 'Pagar' }).click();

  // `expect` do Playwright ESPERA até a condição valer (ou o timeout).
  // Nunca use `waitForTimeout(2000)`: é a origem nº 1 de teste flaky.
  await expect(page.getByRole('heading', { name: 'Pedido confirmado' })).toBeVisible();
  await expect(page).toHaveURL(/\/pedidos\/\d+/);
});
```

### 4.3 As sete regras que separam E2E útil de E2E abandonado

1. **Nunca `sleep`.** Use as esperas da ferramenta, que reavaliam a condição.
2. **Selecione por papel e texto**, não por classe ou XPath. Sobrevive ao redesign, e
   denuncia problema de acessibilidade de quebra.
3. **Cada teste cria os próprios dados.** Depender de "o usuário `teste@ex.br` existe" é
   uma bomba-relógio.
4. **Não encadeie testes.** "Teste 2 usa o pedido criado no teste 1" impede paralelismo e
   produz cascata de falhas.
5. **Teste caminhos, não campos.** Validação de formulário é teste unitário; E2E é para o
   fluxo completo.
6. **Guarde rastro das falhas.** Playwright: `trace: 'on-first-retry'`, vídeo, captura de
   tela. Sem isso, uma falha só no CI é indepurável.
7. **Repetição automática (*retry*) é analgésico, não cura.** Ligue `retries: 2` no CI para
   não travar o time, **e** mantenha um painel de testes instáveis. Teste que só passa na
   segunda tentativa está escondendo alguma coisa — às vezes um bug de corrida de verdade.

### 4.4 Quantos E2E?

Um por **fluxo que gera receita ou que, se quebrar, gera incidente**. Tipicamente entre 5 e
30 numa aplicação de porte médio. Se você tem 300, alguma coisa desceu de camada errada.

---

## 5. Teste de contrato entre implementações

Já visto no [exemplo 10](06-exemplos.md), mas vale o princípio geral:

> Sempre que houver **duas implementações do mesmo contrato** — um fake e um real, SQLite e
> Postgres, memória e Redis — escreva **uma** bateria e rode nas duas.

É o que mantém o dublê honesto. Sem isso, o fake diverge lentamente e a suíte rápida vira
ficção.

---

## 6. O ambiente de teste

### 6.1 Composição com Docker Compose

```yaml
# docker-compose.test.yml
services:
  banco:
    image: postgres:18-alpine
    environment:
      POSTGRES_PASSWORD: teste
      POSTGRES_DB: app_teste
    # tmpfs: o banco inteiro em RAM. Muito mais rápido, e some ao fim.
    tmpfs: [/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 1s
      retries: 30

  app:
    build: .
    depends_on:
      banco: { condition: service_healthy }
    command: pytest -m integracao
```

Dois detalhes que fazem diferença:

- **`tmpfs`** põe o banco em memória: ganho de 3 a 10× em suítes com muita escrita, e nada
  fica no disco.
- **`healthcheck` + `depends_on: condition: service_healthy`** elimina o clássico
  `sleep 10` esperando o banco subir — que é lento quando o banco sobe rápido e insuficiente
  quando sobe devagar.

### 6.2 O ambiente tem de ser descartável

Sintoma de que não é: alguém precisa "limpar o banco de homologação" de vez em quando. Se
existe essa tarefa manual, o ambiente é estado compartilhado, e os testes vão ser instáveis
para sempre.

---

## 7. Os cinco porquês: por que testes de integração são instáveis?

**1. Por quê?** Porque dependem de recursos que não estão sob controle do teste.

**2. Por que não estão sob controle?** Porque são **processos separados**, com ciclo de vida
próprio: o banco pode estar subindo, a porta pode estar ocupada, o container pode estar
baixando a imagem.

**3. Por que isso vira instabilidade e não erro claro?** Porque o teste e o recurso se
comunicam de forma **assíncrona sem sincronização explícita**. O teste tenta conectar; se
chegar cedo demais, falha — e "cedo demais" depende da carga da máquina naquele instante.

**4. Por que a sincronização não é explícita por padrão?** Porque as ferramentas oferecem
"iniciar" e "parar", mas o conceito de **pronto para uso** é específico de cada serviço:
Postgres pronto é `pg_isready`; Kafka pronto é ter eleito líder de partição; sua API pronta
é responder `/health`. Não há sinal universal.

**5. Por que não há um sinal universal?** Porque "pronto" é uma propriedade **semântica** do
serviço, não do processo. O sistema operacional só sabe que o processo existe. **Parada
legítima: é uma limitação conceitual da abstração "processo"** — e é exatamente por isso que
`healthcheck`, *readiness probe* do Kubernetes e as estratégias de espera do Testcontainers
existem, todos reinventando a mesma coisa por serviço.

**Consequência prática:** nunca sincronize com `sleep`. Sincronize com uma **condição
verificável** — e, se ela não existir, crie um endpoint `/health` que a expresse.

---

## 8. Quando integração é o teste **principal**

Nem todo sistema tem uma pirâmide. Três casos em que a maior parte do valor está na
integração:

| Sistema | Por quê |
|---|---|
| *pipeline* de dados (ETL) | a lógica é o SQL/transformação; testar sem dados é testar nada |
| *proxy*, *gateway*, roteador | ele não tem lógica própria; ele **é** a integração |
| aplicação CRUD fina | as regras estão no banco (constraints, triggers) |

Nesses casos, insistir em muitos testes unitários produz testes triviais e uma falsa sensação
de cobertura. Ajuste a carteira ao sistema — ver
[12-tipos-e-piramide.md](12-tipos-e-piramide.md).

---

## Autoteste

1. Cite cinco classes de erro que **só** o teste de integração detecta.
2. Por que SQLite no lugar de Postgres é uma armadilha?
3. Descreva o padrão da transação com rollback e diga quando ele **não** funciona.
4. Por que Testcontainers deve ter escopo de sessão?
5. Quais são os dois problemas de usar dump de produção como dado de teste?
6. Por que nunca fixar a porta num teste de servidor?
7. O `TestClient` do FastAPI sobe um servidor real? O que ele não cobre?
8. Qual é o risco de segurança do VCR, e como mitigá-lo?
9. Enuncie as sete regras de E2E que se sustenta.
10. Por que `retries: 2` é analgésico e não cura?
11. Percorra os cinco porquês da instabilidade de testes de integração até a parada legítima.
12. Cite três tipos de sistema em que a integração é o teste principal.
