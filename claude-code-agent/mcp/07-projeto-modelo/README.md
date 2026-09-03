# Projeto-modelo · `biblioteca-mcp`

`Nível: intermediário` · `Escrito e executado em 01/09/2026`

Um servidor MCP **pequeno, mas inteiro**: consulta de acervo e controle de
empréstimos de uma biblioteca. Roda de verdade, tem teste, trata erro,
tem configuração, e pede confirmação humana antes de alterar dados.

Não é um trecho de código. É o menor sistema que ainda tem tudo que um servidor
MCP de produção precisa ter.

---

## 1. O que ele faz

| Ferramenta | Tipo | O que faz |
|---|---|---|
| `buscar_livros` | leitura | busca por título ou autor; devolve o ISBN |
| `detalhar_livro` | leitura | dados de um livro pelo ISBN exato |
| `emprestar_livro` | **escrita** | empresta um exemplar por 14 dias — **pede confirmação ao usuário** |
| `devolver_livro` | **escrita** | registra a devolução |
| `emprestimos_do_leitor` | leitura | empréstimos abertos de um leitor |
| `estatisticas_do_acervo` | leitura | títulos, exemplares, abertos, atrasados |

| Recurso | O que é |
|---|---|
| `biblioteca://politica` | o regulamento de empréstimo, em texto |

| Prompt | O que é |
|---|---|
| `relatorio_de_atrasos` | roteiro para o modelo escrever o relatório, com tom escolhido pelo usuário |

---

## 2. Pré-requisitos

- **Python 3.10+** — instalado pelo `uv` (o projeto fixa 3.12 no `.python-version`)
- **`uv`** 0.9+ — ver [03 · Instalação §3](../03-instalacao.md#3-python--uv)
- **Node 22.19+** — só para o passo opcional do Inspector
- Nenhum serviço externo. O banco é SQLite, criado sozinho.

---

## 3. Comandos exatos

```bash
cd 07-projeto-modelo
```

```bash
make instalar
```
Cria `.venv/` e instala as dependências travadas.

```bash
make semear
```
Cria `biblioteca.db` com seis títulos brasileiros.
Saída esperada: `acervo criado em biblioteca.db`

```bash
make testar
```
Saída esperada:

```
...............                                                          [100%]
15 passed in 3.96s
```

```bash
make inspecionar
```
Lista as ferramentas pelo MCP Inspector. Saída real (resumida):

```
- buscar_livros          | 234 chars de descrição | ['termo', 'limite']
- detalhar_livro         | 106 chars              | ['isbn']
- emprestar_livro        | 280 chars              | ['isbn', 'leitor']
- devolver_livro         | 154 chars              | ['isbn', 'leitor']
- emprestimos_do_leitor  |  76 chars              | ['leitor']
- estatisticas_do_acervo |  79 chars              | []
```

> Repare: `emprestar_livro` expõe **só** `isbn` e `leitor`. O terceiro parâmetro,
> `confirmacao`, é preenchido pelo **usuário** via MRTR e não aparece no schema —
> o modelo não sabe que existe e não pode forjá-lo. Há um teste que trava isso.

```bash
make rodar
```
Sobe em **stdio**, para um host MCP lançar.

```bash
make http
```
Sobe em `http://127.0.0.1:8931/mcp`. Sonde com:

```bash
curl -sS -X POST http://127.0.0.1:8931/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
  -d '{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{
       "io.modelcontextprotocol/protocolVersion":"2026-07-28",
       "io.modelcontextprotocol/clientCapabilities":{}}}}' | python3 -m json.tool
```

Resposta real:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "cacheScope": "private",
    "capabilities": {
      "prompts": {"listChanged": true},
      "resources": {"listChanged": true, "subscribe": true},
      "tools": {"listChanged": true}
    },
    "instructions": "Use `buscar_livros` para encontrar um livro pelo título ou autor e obter o ISBN. ...",
    "resultType": "complete",
    "supportedVersions": ["2026-07-28"],
    "ttlMs": 0,
    "_meta": {"io.modelcontextprotocol/serverInfo": {
        "name": "biblioteca", "title": "Biblioteca", "version": "1.0.0",
        "description": "Consulta de acervo e controle de empréstimos de uma biblioteca."}}
  }
}
```

Ligar a um host:

```bash
claude mcp add biblioteca -- uv run --directory "$PWD" python servidor.py
```

```bash
make limpar
```

---

## 4. Estrutura, comentada

```
07-projeto-modelo/
├── README.md              este arquivo
├── pyproject.toml         dependências, grupo dev, config do pytest
├── .python-version        3.12 — trava o interpretador
├── .env.exemplo           variáveis; copie para .env e ajuste
├── .gitignore             .venv, *.db, .env — nada disso vai para o git
├── Makefile               o ciclo inteiro em comandos curtos
├── servidor.py            CAMADA MCP: valida, chama o domínio, formata a saída
├── biblioteca/
│   ├── __init__.py
│   ├── config.py          configuração pelo ambiente, com teto próprio
│   └── dados.py           DOMÍNIO: SQL parametrizado, transações, regras
└── testes/
    ├── conftest.py        banco temporário por teste
    └── test_servidor.py   15 testes, pela interface do protocolo
```

**A separação `servidor.py` × `biblioteca/` é a decisão estrutural mais importante.**
Nenhuma regra de negócio mora na camada MCP. Consequências práticas:

- o domínio é testável sem MCP nenhum;
- trocar o transporte (stdio → HTTP) não toca em regra de negócio;
- expor a mesma biblioteca por REST amanhã é escrever outro arquivo fino;
- quando um teste quebra, você sabe se quebrou a regra ou o contrato.

---

## 5. O que cada decisão de projeto ensina

### 5.1 Log em `stderr`, sempre

```python
logging.basicConfig(stream=sys.stderr, ...)
```

Em stdio, `stdout` **é a fita do protocolo**. Um `print()` corrompe a conversa e o
cliente derruba a conexão — com um sintoma péssimo: "conecta e cai", sem erro claro.
A spec reserva `stderr` para log de qualquer nível, não só erro.

### 5.2 `ToolError`, não exceção crua

```python
raise ToolError(f"Não existe livro com ISBN {isbn!r}. Use `buscar_livros` ...")
```

No SDK Python 2.x, **só `ToolError` (e `ResourceError`) têm a mensagem entregue ao
modelo**. Qualquer outra exceção vira `Error executing tool <nome>`, sem texto —
proteção contra vazar caminho de arquivo, SQL ou segredo num *crash*. Levantar
`ToolError` é você declarando "eu previ este caso".

E toda mensagem de erro deste projeto **diz o que fazer em seguida**, nomeando a
ferramenta certa. É isso que permite o modelo se corrigir sem incomodar o usuário.
Há testes que travam exatamente esse texto.

### 5.3 Confirmação humana antes de escrever, via MRTR

```python
def _confirmar_emprestimo(isbn: str, leitor: str):
    return Elicit(f"Confirmar empréstimo do livro {isbn} para {leitor}? ...", Confirmacao)

@server.tool()
def emprestar_livro(isbn, leitor,
                    confirmacao: Annotated[ElicitationResult[Confirmacao],
                                           Resolve(_confirmar_emprestimo)]) -> Emprestimo:
```

Três coisas de uma vez:

1. O parâmetro resolvido **não entra no `inputSchema`** — o modelo não pode preenchê-lo.
2. Sob `2026-07-28` isso vira `resultType: "input_required"`, e o cliente **repete a
   chamada** com a resposta. Não há canal de volta do servidor para o cliente.
3. Recusa do usuário **não altera nada** — e há teste provando que `disponiveis`
   continua em 3.

> ⚠️ Chamar `await ctx.elicit(...)` direto dentro da ferramenta levanta
> `NoBackChannelError` nesta revisão do protocolo. Use `Resolve`/`Elicit`.

### 5.4 Verbos do domínio, nunca `executar_sql`

Não existe ferramenta que aceite SQL. Existem seis verbos do negócio. Se alguém
injetar um prompt malicioso, o pior que consegue é emprestar um livro — não
`DROP TABLE`. **Ferramenta genérica demais é superfície de ataque.**

### 5.5 Defesas que não dependem de disciplina

| Defesa | Onde | Por que não basta "lembrar de fazer certo" |
|---|---|---|
| `mode=ro` no driver para leitura | `dados.conectar` | uma escrita acidental falha no driver, não na revisão de código |
| SQL parametrizado | todo o `dados.py` | há teste que manda `'; DROP TABLE livros; --` e confere que os 6 títulos continuam lá |
| `min_length`/`max_length`/`ge`/`le` no schema | `servidor.py` | o cliente valida **antes** de chegar ao seu código |
| teto duplo em `max_linhas` | `config.py` e nas ferramentas | nem o operador consegue configurar algo que estoure o contexto |
| `AND disponiveis > 0` no `UPDATE` | `dados.emprestar` | duas chamadas concorrentes não emprestam o último exemplar duas vezes |
| `CHECK (disponiveis >= 0 ...)` no esquema | `dados.ESQUEMA` | última linha de defesa, no próprio banco |

### 5.6 Saída estruturada exige tipo declarado

Todas as ferramentas devolvem um `BaseModel`. **Verificado nesta máquina:** anotar o
retorno como `dict` cru **não** gera `outputSchema` e deixa `structuredContent` nulo.
Se você quer que o cliente valide a resposta, declare o modelo.

### 5.7 Ordem determinística

Todo `SELECT` tem `ORDER BY` explícito. Isso torna o teste reprodutível **e** melhora
o cache de prompt do LLM — a spec `2026-07-28` pede ordem determinística em
`tools/list` pela mesma razão.

### 5.8 `instructions` no servidor

```python
instructions=("Use `buscar_livros` ... Só então use `emprestar_livro` ...")
```

É onde se ensina ao modelo a **ordem** de uso das ferramentas. Sem isso ele tenta
`emprestar_livro` com o título em vez do ISBN. Aparece na resposta de `server/discover`.

### 5.9 Configuração pelo ambiente

O host lança o processo; ele não roda `docker run -e`. Toda configuração vem de
variáveis de ambiente, que o host passa em `env`. **Segredo nunca vai em `args`** —
`args` aparece em `ps aux`.

### 5.10 Testes que exercitam o caminho ruim

Dos 15 testes, **9 são de caminho ruim ou de defesa**: ISBN inexistente, sem exemplar,
mesmo leitor duas vezes, devolução sem empréstimo, recusa do usuário, limite absurdo,
termo curto demais, injeção de SQL, e o parâmetro de confirmação que não pode vazar
para o modelo. É neles que mora o valor: o caminho feliz quebra com barulho; o caminho
ruim quebra em silêncio.

---

## 6. O que este projeto **não** tem (de propósito)

Para você não achar que está pronto para produção sem mais nada:

| Falta | Onde aprender |
|---|---|
| autorização (OAuth 2.1, validação de audiência) | [18 · Autorização](../18-autorizacao.md) |
| limite de taxa e tempo máximo de operação | [24 · Operação](../24-operacao-e-producao.md) |
| métricas e trace (OpenTelemetry via `_meta`) | [24 · Operação](../24-operacao-e-producao.md) |
| banco de verdade (Postgres) e pool de conexões | [postgresql](../../postgresql/00-MAPA.md) |
| empacotamento em container | [curso-docker](../../curso-docker/) |
| publicação no MCP Registry | [21 · Registro e distribuição](../21-registro-e-distribuicao.md) |

---

## 7. Exercícios sobre este projeto

1. Acrescente `renovar_emprestimo`, respeitando o item 3 do regulamento (que proíbe
   renovação). Decida: a ferramenta explica a política, ou nem existe? Justifique.
2. Faça `buscar_livros` devolver `resource_link` para `biblioteca://politica` quando
   o termo não encontrar nada.
3. Faça `emprestimos_do_leitor` marcar quais estão atrasados, **sem** acrescentar
   consulta ao banco.
4. Troque SQLite por Postgres mudando **só** `biblioteca/dados.py`. Se você precisou
   tocar em `servidor.py`, a separação estava errada — encontre onde.
5. Escreva um teste que prove que duas chamadas concorrentes ao último exemplar não
   deixam `disponiveis` negativo.
6. Suba com `make http` e escreva um cliente Python que se conecta por
   `Client("http://127.0.0.1:8931/mcp")` e faz o ciclo emprestar→devolver.

---

## 8. Verificação registrada

Executado em **01/09/2026**, Ubuntu 22.04.5 LTS x86-64:

- `uv sync` → ambiente criado com `mcp` 2.1.1, Python 3.12.14
- `uv run pytest` → **15 passed in 3.96s**
- `make inspecionar` → 6 ferramentas listadas, com os schemas acima
- `make http` + `curl server/discover` → resposta real reproduzida na §3
- protocolo negociado: **2026-07-28**

---

**Voltar:** [06 · Exemplos](../06-exemplos.md) · **Próximo:** [10 · Fundamentos](../10-fundamentos.md) · **Índice:** [00-MAPA](../00-MAPA.md)
